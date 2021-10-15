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
"""Executable and reusable sample for listing detections.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#listdetections
"""

import argparse
import datetime
import json
import sys
from typing import Any, Mapping, Optional, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
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
      "-st",
      "--start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=False,
      help="detection start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-et",
      "--end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=False,
      help="detection end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-lb",
      "--list_basis",
      type=str,
      required=False,
      help="list basis (i.e. 'DETECTION_TIME', 'CREATED_TIME')")
  parser.add_argument(
      "-a",
      "--alert_state",
      type=str,
      required=False,
      help="alert state (i.e. 'ALERTING', 'NOT_ALERTING')")

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)

  s, e = parsed_args.start_time, parsed_args.end_time
  if s is not None and s > datetime.datetime.utcnow().astimezone(
      datetime.timezone.utc):
    print("Error: start time should not be in the future")
    return None
  if s is not None and e is not None and s >= e:
    print("Error: start time should not be same as or later than the end time")
    return None
  if parsed_args.alert_state not in (None, "ALERTING", "NOT_ALERTING"):
    print("Error: alert_state should one of ALERTING, NOT_ALERTING, or empty")
    return None
  if parsed_args.list_basis not in (None, "DETECTION_TIME", "CREATED_TIME"):
    print(
        "Error: list_basis should one of DETECTION_TIME, CREATED_TIME, or empty"
    )
    return None

  return parsed_args


def list_detections(
    http_session: requests.AuthorizedSession,
    version_id: str,
    page_size: int = 0,
    page_token: str = "",
    start_time: Optional[datetime.datetime] = None,
    end_time: Optional[datetime.datetime] = None,
    list_basis: str = "",
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
    start_time: The time to start listing detections from, inclusive
      (default = no min detection_start_time).
    end_time: The time to end listing detections to, exclusive
      (default = no max detection_end_time).
    list_basis: A string that determines whether start_time and end_time refer
      to the detection time (DETECTION_TIME) or creation time (CREATED_TIME) of
      the detection results (default = filter by detection time).
    alert_state: A string that filters which detections are returned, based on
      their AlertState: "ALERTING" or "NOT_ALERTING" (default = no filtering).

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
      ("start_time", datetime_converter.strftime(start_time)),
      ("end_time", datetime_converter.strftime(end_time)),
      ("list_basis", list_basis),
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
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  detections, next_page_token = list_detections(session, cli.version_id,
                                                cli.page_size, cli.page_token,
                                                cli.start_time, cli.end_time,
                                                cli.list_basis, cli.alert_state)
  print(json.dumps(detections, indent=2))
  print(f"Next page token: {next_page_token}")
