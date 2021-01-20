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
#
"""Executable and reusable sample for retrieving detection."""

import argparse
import pprint
from typing import Any, Mapping

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def get_detection(http_session: requests.AuthorizedSession, version_id: str,
                  detection_id: str) -> Mapping[str, Any]:
  """Get detection.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: The specific rule version to get detection for.
    detection_id: Id of the detection to get information for.

  Returns:
    Detection information.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = (f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{version_id}/" +
         f"detections/{detection_id}")

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "id": "de_<UUID>",
  #   "type": "RULE_DETECTION",
  #   "createdTime": "yyyy-mm-ddThh:mm:ssZ",
  #   "detectionTime": "yyyy-mm-ddThh:mm:ssZ",
  #   "timeWindow": {
  #     "startTime": "yyyy-mm-ddThh:mm:ssZ",
  #     "endTime": "yyyy-mm-ddThh:mm:ssZ",
  #   }
  #   "collectionElements": [
  #     {
  #       "label": "e1",
  #       "references": [
  #         {
  #           "event": <UDM keys and values / sub-dictionaries>...
  #         },
  #         ...
  #       ],
  #     },
  #     {
  #       "label": "e2",
  #       ...
  #     },
  #     ...
  #   ],
  #   "detection": [
  #     {
  #       "ruleId": "ru_<UUID>",
  #       "ruleName": "<rule_name>",
  #       "ruleVersion": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #       "urlBackToProduct": "<URL>",
  #       "alertState": "ALERTING"/"NOT_ALERTING",
  #       "ruleType": "SINGLE_EVENT"/"MULTI_EVENT",
  #       "detectionFields": [
  #         {
  #           "key": "<field name>",
  #           "value": "<field value>"
  #         }
  #       ]
  #     },
  #   ],
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-vi",
      "--version_id",
      type=str,
      required=True,
      help="version ID ('ru_<UUID>[@v_<seconds>_<nanoseconds>]')")
  parser.add_argument(
      "-di",
      "--detection_id",
      type=str,
      required=True,
      help="detection ID ('de_<UUID>')")
  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  detection = get_detection(session, args.version_id, args.detection_id)
  pprint.pprint(detection)