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
"""Executable and reusable sample for listing detection rules."""

import argparse
import pprint
from typing import Any, Mapping, Sequence, Tuple

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_rules(http_session: requests.AuthorizedSession,
               page_size: int = 0,
               page_token: str = "") -> Tuple[Sequence[Mapping[str, Any]], str]:
  """List detection rules.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: Maximum number of rules to return.
    page_token: Page token from a previous ListRules call used for pagination.

  Returns:
    List of rules and a page token for the next page of results, if there are
    any.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules"
  params_list = [("page_size", page_size), ("page_token", page_token)]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  # Expected server response:
  # {
  #   "rules": [
  #     {
  #       "ruleId": "ru_<UUID>",
  #       "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #       "ruleName": "<rule_name>",
  #       "metadata": {
  #         "<key_1>": "<value_1>",
  #         "<key_2>": "<value_2>",
  #         ...
  #       },
  #       "ruleText": "<rule_content>",
  #       "alertingEnabled": true, <-- IFF alerting is enabled.
  #       "liveRuleEnabled": true, <-- IFF a live rule is enabled.
  #       "versionCreateTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #       "compilationState": "SUCCEEDED"/"FAILED",
  #       "compilationError": "<error_message>" <-- IFF compilation failed.
  #     },
  #     ...
  #   ],
  #   "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  json = response.json()
  return json.get("rules", []), json.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
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
      help="page token from a previous ListRules call used for pagination")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  rules, next_page_token = list_rules(session, args.page_size, args.page_token)
  pprint.pprint(rules)
  print(f"Next page token: {next_page_token}")
