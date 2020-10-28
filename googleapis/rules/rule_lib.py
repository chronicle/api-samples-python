#!/usr/bin/env python3

# Copyright 2020 Google LLC
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
"""Library for accessing the Chronicle Rules API."""

import json
import logging
import os
import os.path
import pprint
import sys
import time

# Imports required for the sample - Google Auth and API Client Library Imports.
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
  """Wrapper library for the rules engine API.

  The URL used is logged at the INFO level.
  """

  def __init__(self):
    self.backstory_api_url = API_URL
    self.client, self.service_account_credentials = (
        self._create_authenticated_http_client())

  def _create_authenticated_http_client(self):
    """Creates HTTP client using local credential file storing OAuth JSON."""
    # Constants.
    scopes = ["https://www.googleapis.com/auth/chronicle-backstory"]
    # Or the location you placed your JSON file.
    service_account_file = os.path.abspath(
        os.path.join(os.environ["HOME"], "bk_credentials.json"))
    if not os.path.exists(service_account_file):
      raise ValueError(f"missing service account file: {service_account_file}")

    # Create a credential using Google Developer Service Account Credential and
    # Backstory API Scope.
    credentials = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=scopes)

    # Build a Http client that can make authorized OAuth requests.
    return _auth.authorized_http(credentials), credentials

  def _parse_response(self, resp):
    """Prints the request URL & response/error returned by the HTTP client.

    Args:
      resp: HTTP response returned by the HTTP client.

    Returns:
       Result as an object.

    Raises:
      ValueError: Problem with the request or the conversion to an object.
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
    if 200 <= transport.status < 300:
      return rpc_obj

    # Otherwise, something went wrong.
    _LOGGER_.error("Problem with the rpc call:")
    _LOGGER_.error("  rpc: %s", pprint.pformat(rpc_obj))
    _LOGGER_.error("  transport: %s", pprint.pformat(transport))

    raise ValueError(("problem with rpc call", rpc_obj, transport))

  def _stream(self, continuation_time, url, integrations):
    """Calls the streaming RPC in a retry loop with exponential backoff.

    Processes a stream of batches. A batch is a dictionary.

    A batch might have the key "error"; if it does, you should retry connecting
    with exponential backoff.

    A batch might be an empty dictionary; these are meant as keep-alive
    heartbeats from the server, which your client can ignore.

    If none of the above apply, a batch will have a key "continuationTime"
    (see the documentation of the continuation_time argument below). It will
    optionally have a key such as "notifications" or "detections" whose value is
    a list of notifications or alerts from Rules Engine.

    Args:
      continuation_time: String containing a time in RFC 3339 format, to request
        all notifications created at or after a time; can be omitted to request
        notifications created at or after the current time.
      url: String representing the URL endpoint.
      integrations: List of functions that integrate the stream results with
        other platforms. These functions must have one argument, a dict
        containing a batch from parse_stream.

    Raises:
      RuntimeError: Hit retry limit after multiple consecutive failures
        without success.
    """
    # Our retry loop uses exponential backoff. For simplicity, we retry for all
    # types of errors, which is fine because we've set a retry limit.
    max_consecutive_failures = 7
    consecutive_failures = 0
    while True:
      if consecutive_failures > max_consecutive_failures:
        raise RuntimeError("exiting retry loop. consecutively failed " +
                           f"{consecutive_failures} times without success")

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
      # client-side timeout; if more than 60s pass between messages from the
      # server, the client cancels connection (then retries).
      with requests.post(
          url, stream=True, data=data, headers=headers, timeout=60) as response:
        _LOGGER_.info(
            "initiated connection to notifications stream with request: %s",
            data)
        if response.status_code != 200:
          disconnection_reason = (
              "connection refused with " +
              f"status={response.status_code}, error={response.text}")
        else:
          for batch in rule_utils.parse_stream(response):
            if not batch:
              _LOGGER_.info("Got empty heartbeat")
              continue
            if "error" in batch:
              disconnection_reason = "connection closed with error: {}".format(
                  json.dumps(batch["error"], indent="\t"))
              break
            else:
              consecutive_failures = 0

            # Update continuation_time so that when we retry after a broken
            # connection, we resume receiving results from where we left off.
            continuation_time = batch["continuationTime"]
            _LOGGER_.info("Got response with continuationTime=%s",
                          continuation_time)

            # Process results.
            for integration in integrations:
              integration(batch)

      # When we reach this line of code, we have disconnected.
      consecutive_failures += 1
      _LOGGER_.error(disconnection_reason if disconnection_reason else
                     "connection unexpectedly closed")

  def stream_rule_notifications(self, continuation_time):
    """Calls StreamRuleNotifications RPC in retry loop with exponential backoff.

    The StreamRuleNotifications RPC streams notifications from Rules Engine V1.

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
      continuation_time: String containing a time in RFC 3339 format, to request
        all notifications created at or after a time; can be omitted to request
        notifications created at or after the current time.

    Raises:
      RuntimeError: Hit retry limit after multiple consecutive failures
        without success.
    """
    url = "{}/rules:streamRuleNotifications".format(self.backstory_api_url)
    _LOGGER_.info("stream rule notifications: %s ", url)
    self._stream(continuation_time, url, [
        rule_notification_integrations.print_notifications,
        rule_notification_integrations.slack_webhook_notifications
    ])

  def stream_detections(self, continuation_time):
    """Calls the StreamDetections RPC in a retry loop with exponential backoff.

    The StreamDetections RPC streams alerts from Rules Engine V2.

    Example detection batch without detections list:
      {
        'continuationTime': '2019-04-15T21:59:17.081331Z'
      }

    Example detection batch with detections list:
      {
        'continuationTime': '2019-05-29T05:00:04.123073Z',
        'detections': [
          {
            "metadata": {
              "ruleId": "ru_bce9e2a0-0c7a-48f0-9912-dbb40259405e",
              "rule": "NameOfRule",
              "versionTime": "2020-09-08T20:34:19.543407Z"
            },
            "detectionInfo": {
              # The 'fields' key will be omitted for single-event rules.
              "fields": [
                {
                  "name": "match_variable",
                  "stringVal": "10.142.0.51"
                }
              ],
              "timeWindow": {
                "startTime": "2020-09-08T19:04:09.881104Z",
                "endTime": "2020-09-08T19:04:09.881104Z"
              },
              "resultEvents": {
                "e": {
                  "events": [ ... event in udm format ... ]
                }
              }
            }
          }, ... ]
      }


    Args:
      continuation_time: String containing a time in RFC 3339 format, to request
        all alerting detections created at or after a time; can be omitted to
        request detections created at or after the current time.

    Raises:
      RuntimeError: Hit retry limit after multiple consecutive failures
        without success.
    """
    url = "{}/rules:streamDetections".format(self.backstory_api_url)
    _LOGGER_.info("stream detections: %s ", url)
    self._stream(continuation_time, url, [
        rule_notification_integrations.print_detections,
        rule_notification_integrations.slack_webhook_detections
    ])


if __name__ == "__main__":
  sys.exit("For use as a library. Please import instead.")
