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
"""Executable and reusable sample for creating a detection rule."""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_rule(http_session: requests.AuthorizedSession,
                rule_content: str) -> Mapping[str, Any]:
  """Creates a new detection rule to find matches in logs.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_content: Content of the new detection rule, used to evaluate logs.

  Returns:
    New detection rule.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules"
  body = {"rule_text": rule_content}

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
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: python3 create_rule.py -f <path>
      # STDIN example: cat rule.txt | python3 create_rule.py -f -
      help="path of a file with the desired rule's content, or - for STDIN")

  args = parser.parse_args()
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_rule = create_rule(session, args.rule_file.read())
  print(json.dumps(new_rule, indent=2))
