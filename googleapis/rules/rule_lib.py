#!/usr/bin/env python3
# Copyright 2020 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Lint as: python3
"""Library for accessing backstory"s Rules API.

This library is for python3.
"""

import json
import logging
import os
import os.path
import pprint
import sys
import time
import urllib

# Imports required for the sample - Google Auth and API Client Library
# Imports.
# Get these packages from https://pypi.org/project/google-api-python-client/
# or run $ pip install google-api-python-client from your terminal.
from googleapiclient import _auth
import requests
import rule_notification_integrations
import rule_utils

from google.oauth2 import service_account

# Give this library a logger with a unique name.
_LOGGER_ = logging.getLogger(__name__)

API_URL = "https://backstory.googleapis.com/v1"


class RuleLib():
  """A wrapper library for the rules engine API.

  The url used is logged at the INFO level.
  """

  def __init__(self):
    self.backstory_api_url = API_URL
    self.client, self.service_account_credentials = self._create_authenticated_http_client()

  def _create_authenticated_http_client(self):
    """Create the http client using local credential file storing oauth json."""
    # Constants
    scopes = ["https://www.googleapis.com/auth/chronicle-backstory"]
     # Or the location you placed your JSON file.
    service_account_file = os.path.abspath(
        os.path.join(os.environ["HOME"], "bk_credentials.json"))
    if not os.path.exists(service_account_file):
      raise ValueError(
          "missing service account file: %s" % service_account_file)

    # Create a credential using Google Developer Service Account Credential and
    # Backstory API Scope.
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)

    # Build a Http client that can make authorized OAuth requests.
    return _auth.authorized_http(credentials), credentials

  def _parse_response(self, resp):
    """Print the request url & response/error returned by the http client.

    Args:
      resp: the http response returned by the http client.

    Returns:
       result as a python object.

    Raises:
      ValueError - problem with the request or the conversion to python object.
    """
    # The response is a tuple where:
    #   resp[0] is a python dictionary with information about the
    #     http side of things (aka the transport) such as the http status.
    #   resp[1] is a json string response from the actual rpc call itself.
    transport = resp[0]
    rpc_json = resp[1]
    _LOGGER_.info("response - transport %s", pprint.pformat(transport))
    _LOGGER_.info("response - rpc_json %s", rpc_json)

    rpc_obj = json.loads(rpc_json)
    # If the response shows success...
    if  200 <= transport.status < 300:
      return rpc_obj

    # Otherwise, something went wrong.
    _LOGGER_.error("Problem with the rpc call:")
    _LOGGER_.error("  rpc: %s", pprint.pformat(rpc_obj))
    _LOGGER_.error("  transport: %s", pprint.pformat(transport))

    raise ValueError(("problem with rpc call", rpc_obj, transport))

  def stream_rule_notifications(self, continuation_time):
    """Call the StreamRuleNotifications RPC in a retry loop with exponential backoff.

    Processes a stream of rule notification batches.
    A notification batch is a dictionary.

    A notification batch might have the key "error"; if it does, you should
    retry connecting with exponential backoff.

    A notification batch might be an empty dictionary; these are meant as
    keep-alive heartbeats from the server, which your client can ignore.

    If none of the above apply, a notification batch will have a key
    "continuationTime" (see the documentation of the continuation_time
    argument below). It will optionally have a key "notifications", whose
    value is a list of rule notifications (see example below for the
    format of a rule notification).

    Example notification batch without notifications list:
      {
        'continuationTime': '2019-04-15T21:59:17.081331Z'
      }

    Example notification batch with notifications list:
      {
        'continuationTime': '2019-05-29T05:00:04.123073Z',
        'notifications': [
          {
            'result': {'match': { ... single event in udm format ... } },
            'ruleId': 'ru_13f58277-8d41-45b2-ab6b-1addc4e3ca0e',
            'rule': 'NameOfRule',
            'operation':
            'operations/rulejob_jo_fd826fb3-fdfa-40d0-8681-482fc014ef62'
          }, ... ]
      }

    Args:
      continuation_time: a string containing a time in rfc3339 format, to
        request all notifications created at or after a time; can be omitted to
        request notifications created at or after the current time

    Returns:
      None

    Raises:
      RuntimeError - Hit retry limit after multiple consecutive failures
        without success
    """

    url = "{}/rules:streamRuleNotifications".format(self.backstory_api_url)
    _LOGGER_.info("stream rule notifications: %s ", url)

    # Our retry loop uses exponential backoff. For simplicity, we retry for all
    # types of errors, which is fine because we've set a retry limit.
    max_consecutive_failures = 7
    consecutive_failures = 0
    while True:
      if consecutive_failures > max_consecutive_failures:
        raise RuntimeError(
            "exiting retry loop. consecutively failed {} times without success"
            .format(consecutive_failures))

      if consecutive_failures:
        sleep_duration = 2**consecutive_failures
        _LOGGER_.info("sleeping %d seconds before retrying", sleep_duration)
        time.sleep(sleep_duration)

      data = {} if not continuation_time else {
          "continuationTime": continuation_time
      }
      headers = {}
      _auth.apply_credentials(self.service_account_credentials, headers)

      disconnection_reason = None
      # Heartbeats are sent by the server, approximately every 15s. We impose a
      # client-side timeout; if more than 60s pass between messages from the server,
      # the client cancels connection (then retries).
      with requests.post(url, stream=True, data=data, headers=headers, timeout=60) as response:
        _LOGGER_.info(
            "initiated connection to notifications stream with request: %s",
            data)
        if response.status_code != 200:
          disconnection_reason = "connection refused with status={}, error={}".format(
              response.status_code, response.text)
        else:
          for notification_batch in rule_utils.parse_notification_stream(response):
            if not notification_batch:
              _LOGGER_.info("Got empty heartbeat")
              continue
            if "error" in notification_batch:
              disconnection_reason = "connection closed with error: {}".format(
                  json.dumps(notification_batch["error"], indent="\t"))
              break
            else:
              consecutive_failures = 0

            # Update continuation_time so that when we retry after a broken connection,
            # we resume receiving results from where we left off.
            continuation_time = notification_batch["continuationTime"]
            _LOGGER_.info("Got response with continuationTime=%s", continuation_time)

            # Process received notifications.
            rule_notification_integrations.print_notifications(notification_batch)
            rule_notification_integrations.slack_webhook(notification_batch)

      # When we reach this line of code, we have disconnected.
      consecutive_failures += 1
      _LOGGER_.error(disconnection_reason if disconnection_reason else
                     "connection unexpectedly closed")

  def get_rule(self, rule_id):
    r"""Call the GetRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_

    Returns:
    {
      'rule': ' ... text of rule include \n for new line ...',
      'ruleId':'ru_6e3c6f79-3288-441b-9e9c-15029b98fc6a'
    }
    """
    url = "{}/rules/{}".format(self.backstory_api_url, rule_id)
    _LOGGER_.info("get rule: %s ", url)

    # Make a request
    response = self.client.request(url, "GET")
    return self._parse_response(response)

  def list_rules(self):
    """Call the ListRules RPC.

    Returns:
      {'rules': [
          {
            'rule': '...rule text...",
            'ruleId': 'ru_13f58277-8d41-45b2-ab6b-1addc4e3ca0e',
          }, ... ]
      }
    """
    url = "{}/rules".format(self.backstory_api_url)
    _LOGGER_.info("list rule: %s ", url)

    # Make a request
    response = self.client.request(url, "GET")
    return self._parse_response(response)

  def create_rule(self, rule_text):
    """Call the CreateRule RPC.

    This function requires the file path (to rule) to be passed in as a command
    line arg, -rp.

    Args:
      rule_text: rule as a string

    Returns:
      {'rule': '...rule text...',
       'ruleId': 'ru_ce0717ab-18a5-453e-a958-d528dad5d1c0'
      }
    """
    if not rule_text:
      raise ValueError("Empty rule")

    url = "{}/rules".format(self.backstory_api_url)
    _LOGGER_.info("create rule: %s ", url)

    # Construct the post body for the create rule request.
    body = {
        "rule.rule": rule_text
    }
    # Make a request
    response = self.client.request(
        url,
        method="POST",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        body=urllib.parse.urlencode(body))
    return self._parse_response(response)

  def create_rule_path(self, rule_path):
    """Call the CreateRule RPC.

    This function requires the file path (to rule) to be passed in as a command
    line arg, -rp.

    Args:
      rule_path: path to the rule to be uploaded

    Returns:
      {'rule': '...rule text...',
       'ruleId': 'ru_ce0717ab-18a5-453e-a958-d528dad5d1c0'
      }
    """
    if not rule_path:
      raise ValueError("Missing rule path")
    with open(rule_path, "r") as fd:
      contents = fd.read()

    return self.create_rule(contents)

  def update_rule(self, rule_id, rule_text):
    """Call the UpdateRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_
      rule_text: rule as a string

    Returns:
      {'rule': '...rule text...',
       'ruleId': 'ru_ce0717ab-18a5-453e-a958-d528dad5d1c0'
      }
    """
    if not rule_text:
      raise ValueError("Missing rule text")
    if not rule_id:
      raise ValueError("Missing rule id")
    url = "{}/rules/{}".format(self.backstory_api_url, rule_id)
    _LOGGER_.info("update rule: %s ", url)

    # Construct the post body for the update rule request.
    body = {
        "rule.rule": rule_text,
        "update_mask.paths": "rule.rule"
    }
    # Make a request
    response = self.client.request(
        url,
        method="PATCH",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        body=urllib.parse.urlencode(body))
    return self._parse_response(response)

  def update_rule_path(self, rule_id, rule_path):
    """Call the UpdateRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_
      rule_path: path to the rule to be uploaded

    Returns:
      {'rule': '...rule text...',
       'ruleId': 'ru_ce0717ab-18a5-453e-a958-d528dad5d1c0'
      }
    """
    if not rule_path:
      raise ValueError("Missing rule path")
    if not rule_id:
      raise ValueError("Missing rule id")
    with open(rule_path, "r") as fd:
      contents = fd.read()
    return self.update_rule(rule_id, contents)

  def delete_rule(self, rule_id):
    """Call the DeleteRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_

    Returns:
      An empty python dictionary object.
    """
    if not rule_id:
      raise ValueError("Missing rule id")
    url = "{}/rules/{}".format(self.backstory_api_url, rule_id)
    _LOGGER_.info("delete rule: %s ", url)

    # Make a request
    response = self.client.request(url, "DELETE")
    return self._parse_response(response)

  def run_rule(self, rule_id, start_time, end_time):
    """Call the RunRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_
      start_time: start time for job in rfc3339 format.
      end_time: end time for job in rfc3339 format.

    Returns:
      {'name': 'operations/rulejob_jo_0440fca2-ff4b-4067-b16a-e8bc2368fc15'}
    """
    if not rule_id or not start_time or not end_time:
      raise ValueError(
          "Missing one or more of rule id, start time, or end time")

    url = "{}/rules/{}:run".format(self.backstory_api_url, rule_id)
    _LOGGER_.info("run rule: %s ", url)

    # Construct the post body for the create rule request.
    body = {
        "event_start_time": start_time,
        "event_end_time": end_time
    }
    # Make a request
    response = self.client.request(
        url,
        method="POST",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        body=urllib.parse.urlencode(body))
    return self._parse_response(response)

  def enable_live_rule(self, rule_id):
    """Call the EnableLiveRule RPC.

    Args:
      rule_id: A rule id string that begins with ru_

    Returns:
      {'name': 'operations/rulejob_jo_0440fca2-ff4b-4067-b16a-e8bc2368fc15'}
    """
    if not rule_id:
      raise ValueError(
          "Missing rule id")

    url = "{}/rules/{}:enableLiveRule".format(self.backstory_api_url, rule_id)
    _LOGGER_.info("enable live rule: %s ", url)

    # Construct the post body for the create rule request.
    body = {}

    # Make a request
    response = self.client.request(
        url,
        method="POST",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        body=urllib.parse.urlencode(body))
    return self._parse_response(response)

  def list_results(self, operation_id, page_size=0, page_token=''):
    """Call the ListResults RPC.

    Args:
      operation_id: an operation id

    Returns:
      {'results': [
             {'match': {
               ... sinlge event in udm format ...
                       }
              },
           ...
           ]
      }
    """
    if not operation_id:
      raise ValueError("Missing operation id")
    url = "{}/rules_results?name={}&page_size={}&page_token={}".format(
        self.backstory_api_url, operation_id, page_size, page_token)
    _LOGGER_.info("list results: %s ", url)

    response = self.client.request(url, "GET")
    return self._parse_response(response)

  def get_operation(self, operation_id):
    """Call the GetOperation RPC.

    Args:
      operation_id: an operation id

    Returns:
      {'done': True,
         'error': {'code': 10, 'message': 'RESULT_LIMIT_REACHED'},
         'metadata': {'@type': 'type.googleapis.com/chronicle.backstory.v1.RunRuleMetadata',
                      'eventEndTime': '2019-11-25T00:00:00Z',
                      'ruleId': 'ru_d1b69671-10d8-451a-9398-b6a254aa22e0',
                      'eventStartTime': '2019-11-11T17:31:59Z'},
         'name': 'operations/rulejob_jo_1b6c6267-53ed-4667-819b-a024ea8bfbe2'
      }
    """
    if not operation_id:
      raise ValueError("Missing operation id")
    url = "{}/{}".format(self.backstory_api_url, operation_id)
    _LOGGER_.info("get operations: %s ", url)

    # Make a request
    response = self.client.request(url, "GET")
    return self._parse_response(response)

  def list_operations(self):
    """Call the ListOperations RPC.

    Sadly, done is only populated if the job is done. Not done needs to be
    inferred. Similar for success which needs to be inferred by a
    lack of error. Not clear why eventStartTime and eventEndTime is in some of
    them and not others.

    Returns:
      [ {'done': True,
         'error': {'code': 10, 'message': 'RESULT_LIMIT_REACHED'},
         'metadata': {'@type': 'type.googleapis.com/chronicle.backstory.v1.RunRuleMetadata',
                      'eventEndTime': '2019-11-25T00:00:00Z',
                      'ruleId': 'ru_d1b69671-10d8-451a-9398-b6a254aa22e0',
                      'eventStartTime': '2019-11-11T17:31:59Z'},
         'name': 'operations/rulejob_jo_1b6c6267-53ed-4667-819b-a024ea8bfbe2'},
        {'done': True,
         'metadata': {'@type': 'type.googleapis.com/chronicle.backstory.v1.RunRuleMetadata',
                      'ruleId': 'ru_c76616b8-40dd-4dc7-8b11-c4f7df4c9cef'},
         'name': 'operations/rulejob_jo_2047d71c-28e9-4fbb-adee-2f0847eefd2e',
         'response': {'@type': 'type.googleapis.com/chronicle.backstory.v1.RunRuleResponse'}},
        {'metadata': {'@type': 'type.googleapis.com/chronicle.backstory.v1.RunRuleMetadata',
                      'ruleId': 'ru_226616b9-466d-4777-8991-11f7df4c9c44'},
         'name': 'operations/rulejob_jo_2047d71c-28e9-4fbb-adee-2f0847eefd2e'},
        ...
       ]

    Note that in the above example output, the first two operations are done
    (there is a 'done':True entry in the dictionary, and there is a populated
    'response'), while the third is not (no 'done' or 'response' entries).
    """
    url = "{}/operations".format(self.backstory_api_url)
    _LOGGER_.info("list operations: %s ", url)

    # Make a request
    response = self.client.request(url, "GET")
    return self._parse_response(response)

  def wait_operation(self, operation_id):
    """Implement a local wait for an operation with GetOperation loop.

    Args:
      operation_id: an operation id

    Returns:
      None
    """
    if not operation_id:
      raise ValueError("Missing operation_id")
    # Make a request
    sleep, max_sleep = 2, 120
    while True:
      # This raises a ValueError() if there is a problem.
      # We can catch this and throw a different error if that is more
      # compatible with the wait operation call when it is implemented.
      rule = self.get_operation(operation_id)
      if rule.get("metadata").get("@type") == "type.googleapis.com/chronicle.backstory.v1.EnableLiveRuleMetadata":
        break
      if rule.get("done", False):
        break
      _LOGGER_.info("Sleeping for %d seconds", sleep)
      time.sleep(sleep)
      sleep = sleep * 2
      if sleep > max_sleep:
        sleep = max_sleep
    _LOGGER_.info("Operation completed:\n%s", rule)

  def delete_operation(self, operation_id):
    """Call the DeleteOperation RPC.

    Args:
      operation_id: an operation id

    Returns:
      An empty python dictionary object.
    """
    if not operation_id:
      raise ValueError("Missing operation_id")
    url = "{}/{}".format(self.backstory_api_url, operation_id)
    _LOGGER_.info("delete operation: %s ", url)

    # Make a request
    response = self.client.request(url, "DELETE")
    return self._parse_response(response)

  def cancel_operation(self, operation_id):
    """Call the CancelOperation RPC.

    Args:
      operation_id: an operation id

    Returns:
      python object
    """
    if not operation_id:
      raise ValueError("Missing operation_id")

    url = "{}/{}:cancel".format(self.backstory_api_url, operation_id)
    _LOGGER_.info("list results: %s ", url)

    # Make a request
    response = self.client.request(
        url,
        method="POST",
        headers={"Content-type": "application/x-www-form-urlencoded"},
        body=None)
    return self._parse_response(response)

if __name__ == "__main__":
  sys.exit("For use as a library. Please import instead.")
