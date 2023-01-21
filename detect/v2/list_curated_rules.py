#!/usr/bin/env python3

# Copyright 2023 Google LLC
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
"""Executable and reusable sample for listing curated rules.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#listcuratedrules
"""

import argparse
import json
from typing import Any, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

_chronicle_api_base_url = "https://backstory.googleapis.com"


def list_curated_rules(
    http_session: requests.AuthorizedSession,
    page_size: int = 0,
    page_token: str = "") -> Tuple[Sequence[Mapping[str, Any]], str]:
  """List curated rules.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: Maximum number of rules to return. Must be non-negative, and is
      capped at a server-side limit of 1000. Optional - a server-side default of
      100 is used if the size is 0 or a None value.
    page_token: Page token from a previous ListCuratedRules call used for
      pagination. Optional - the first page is retrieved if the token is the
      empty string or a None value.

  Returns:
    List of curated rules and a page token for the next page of rules, if there
    are any.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{_chronicle_api_base_url}/v2/detect/curatedRules"
  params_list = [("page_size", page_size), ("page_token", page_token)]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  # Expected server response:
  # {
  #   "curatedRules": [
  #     {
  #       "ruleId": "ur_xxx",
  #       "ruleName": "<rule_name>",
  #       "metadata": { <-- IFF there is additional metadata
  #         "<key_1>": "<value_1>",
  #         "<key_2>": "<value_2>",
  #         ...
  #       },
  #       "severity": "Info"/"Low"/"High",
  #       "ruleType": "MULTI_EVENT"/"SINGLE_EVENT",
  #       "precision": "PRECISE"/"BROAD",
  #       "tactics": [
  #         "TA####"
  #       ],
  #       "techniques": [
  #         "T####"
  #       ],
  #       "updateTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #       "ruleSet": "<rule_set_uuid>",
  #       "description": "<rule_description>",
  #     },
  #     ...
  #   ],
  #   "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("curatedRules", []), j.get("nextPageToken", "")


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
      help="page token from a previous ListCuratedRules call used for pagination"
  )

  args = parser.parse_args()
  _chronicle_api_base_url = regions.url(_chronicle_api_base_url, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  curated_rules, next_page_token = list_curated_rules(session, args.page_size,
                                                      args.page_token)
  print(json.dumps(curated_rules, indent=2))
  print(f"Next page token: {next_page_token}")
