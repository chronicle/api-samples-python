#!/usr/bin/env python3

# Copyright 2021 Google LLC
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
#
"""Executable and reusable sample for listing detections."""

import argparse
import datetime
import json
from typing import Any, Mapping, Optional, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_detections(
    http_session: requests.AuthorizedSession,
    version_id: str,
    page_size: int = 0,
    page_token: str = "",
    detection_start_time: Optional[datetime.datetime] = None,
    detection_end_time: Optional[datetime.datetime] = None,
    alert_state: str = "") -> Tuple[Sequence[Mapping[str, Any]], str]:
  """Retrieves all the detections of the specified version_id.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: Unique ID of the detection rule to list detections for.
      Valid version ID formats:
        Detections for a specific rule version:
        "ru_<UUID>@v_<seconds>_<nanoseconds>"
        Detections for the latest version of a rule: "ru_<UUID>"
        Detections across all versions of a rule: "ru_<UUID>@-"
        Detections across all rules and all versions: "-"
    page_size: Maximum number of detections in the response.
      Must be non-negative, and is capped at a server-side limit of 1000.
      Optional - we use a server-side default of 100 if the size is 0 or a
      None value.
    page_token: Base64-encoded string token to retrieve a specific page of
      results. Optional - we retrieve the first page if the token is an empty
      string or a None value.
    detection_start_time: The time to start listing detections from, inclusive
      (default = no min detection_start_time).
    detection_end_time: The time to end listing detections to, exclusive
      (default = no max detection_end_time).
    alert_state: A string that filters which detections are returned by their
      AlertState (i.e. 'ALERTING', 'NOT_ALERTING') (default = no filter on
      alert_state).

  Returns:
    All the detections (within the defined page) ordered by descending
    detection_time, as well as a Base64 token for getting the detections of the
    next page (an empty token string means the currently retrieved page is the
    last one).

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{version_id}/detections"
  params_list = [
      ("page_size", page_size),
      ("page_token", page_token),
      ("detection_start_time",
       datetime_converter.strftime(detection_start_time)),
      ("detection_end_time", datetime_converter.strftime(detection_end_time)),
      ("alert_state", alert_state),
  ]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  # Expected server response:
  # {
  #   "detections": [
  #     {
  #       "id": "de_<UUID>",
  #       "type": "RULE_DETECTION",
  #       "createdTime": "yyyy-mm-ddThh:mm:ssZ",
  #       "detectionTime": "yyyy-mm-ddThh:mm:ssZ",
  #       "timeWindow": {
  #         "startTime": "yyyy-mm-ddThh:mm:ssZ",
  #         "endTime": "yyyy-mm-ddThh:mm:ssZ",
  #       }
  #       "collectionElements": [
  #         {
  #           "label": "e1",
  #           "references": [
  #             {
  #               "event": <UDM keys and values / sub-dictionaries>...
  #             },
  #             ...
  #           ],
  #         },
  #         {
  #           "label": "e2",
  #           ...
  #         },
  #         ...
  #       ],
  #       "detection": [
  #         {
  #           "ruleId": "ru_<UUID>",
  #           "ruleName": "<rule_name>",
  #           "ruleVersion": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #           "urlBackToProduct": "<URL>",
  #           "alertState": "ALERTING"/"NOT_ALERTING",
  #           "ruleType": "SINGLE_EVENT"/"MULTI_EVENT",
  #           "detectionFields": [
  #             {
  #               "key": "<field name>",
  #               "value": "<field value>"
  #             }
  #           ]
  #         },
  #       ],
  #     },
  #     ...
  #   ],
  #   "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("detections", []), j.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-vi",
      "--version_id",
      type=str,
      required=True,
      help=("version ID of the rule to list detections for "
            "('- | ru_<UUID>@- | ru_<UUID>[@v_<seconds>_<nanoseconds>]')"))
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of rules to return")
  parser.add_argument(
      "-t",
      "--page_token",
      type=str,
      required=False,
      help="page token from a previous ListDetections call used for pagination")
  parser.add_argument(
      "-dst",
      "--detection_start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=False,
      help="detection start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-det",
      "--detection_end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=False,
      help="detection end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-a",
      "--alert_state",
      type=str,
      required=False,
      help="alert state (i.e. 'ALERTING', 'NOT_ALERTING')")

  args = parser.parse_args()
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  detections, next_page_token = list_detections(session, args.version_id,
                                                args.page_size, args.page_token,
                                                args.detection_start_time,
                                                args.detection_end_time,
                                                args.alert_state)
  print(json.dumps(detections, indent=2))
  print(f"Next page token: {next_page_token}")
