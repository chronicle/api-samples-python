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
"""Executable and reusable sample for listing detection rules.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#listrules
"""

import argparse
import json
from typing import Any, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_rules(
    http_session: requests.AuthorizedSession,
    page_size: int = 0,
    page_token: str = "",
    archive_state: str = "") -> Tuple[Sequence[Mapping[str, Any]], str]:
  """List detection rules.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: Maximum number of rules to return.
      Must be non-negative, and is capped at a server-side limit of 1000.
      Optional - a server-side default of 100 is used if the size is 0 or a
      None value.
    page_token: Page token from a previous ListRules call used for pagination.
      Optional - the first page is retrieved if the token is the empty string
      or a None value.
    archive_state: The archive state to filter rules by (i.e. 'ARCHIVED').
      Optional - if unspecified, only rules with ACTIVE state are returned.

  Returns:
    List of rules and a page token for the next page of rules, if there are
    any.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules"
  params_list = [("page_size", page_size), ("page_token", page_token),
                 ("state", archive_state)]
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
  #       "compilationError": "<error_message>", <-- IFF compilation failed.
  #       "archivedTime": "yyyy-mm-ddThh:mm:ss.ssssssZ", <-- IFF archived.
  #       "ruleType": "MULTI_EVENT"/"SINGLE_EVENT",
  #     },
  #     ...
  #   ],
  #   "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("rules", []), j.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
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
  parser.add_argument(
      "-as",
      "--archive_state",
      type=str,
      required=False,
      help="archive state (i.e. 'ACTIVE', 'ARCHIVED', 'ALL')")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  rules, next_page_token = list_rules(session, args.page_size, args.page_token,
                                      args.archive_state)
  print(json.dumps(rules, indent=2))
  print(f"Next page token: {next_page_token}")
