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
"""Executable and reusable sample for creating a new rule version.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#createruleversion
"""

import argparse
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_rule_version(http_session: requests.AuthorizedSession, rule_id: str,
                        rule_content: str) -> Mapping[str, Any]:
  """Creates a new rule version for a specific rule with given content.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to create a new version for
      ("ru_<UUID>").
    rule_content: Content of the new detection rule, used to evaluate logs.

  Returns:
    VersionId of the updated rule ("ru_<UUID>@v_<seconds>_<nanoseconds>").

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{rule_id}:createVersion"
  body = {"ruleText": rule_content}

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "ruleId": "ru_<UUID>",
  #   "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #   "ruleName": "<rule_name>",
  #   "metadata": {
  #     "<key_1>": "<value_1>",
  #     "<key_2>": "<value_2>",
  #     ...
  #   },
  #   "ruleText": "<rule_content>",
  #   "alertingEnabled": true, <-- IFF alerting is enabled.
  #   "liveRuleEnabled": true, <-- IFF a live rule is enabled.
  #   "versionCreateTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "compilationState": "SUCCEEDED"/"FAILED",
  #   "compilationError": "<error_message>", <-- IFF compilation failed.
  #   "archivedTime": "yyyy-mm-ddThh:mm:ss.ssssssZ", <-- IFF archived.
  #   "ruleType": "MULTI_EVENT"/"SINGLE_EVENT",
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()["versionId"]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: python3 create_rule_version.py -ri <rule_id> -f <path>
      # STDIN example:
      #   cat rule.txt | python3 create_rule_version.py -ri <rule_id> -f -
      help="path of a file with the desired rule's content, or - for STDIN")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_version_id = create_rule_version(session, args.rule_id,
                                       args.rule_file.read())
  print(new_version_id)
