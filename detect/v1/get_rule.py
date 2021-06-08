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
"""Executable and reusable sample for retrieving a detection rule."""

import argparse
import json
import re

from google.auth.transport import requests

from common import chronicle_auth

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

RULE_ID_PATTERN = re.compile(r"ru_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
                             r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def get_rule(http_session: requests.AuthorizedSession, rule_id: str) -> str:
  """Retrieves the content of a specific detection rule.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to retrieve ("ru_<UUID>").

  Returns:
    Content of the requested detection rule, which is used to evaluate logs.

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not RULE_ID_PATTERN.fullmatch(rule_id):
    raise ValueError(f"Invalid detection rule ID: '{rule_id}' != 'ru_<UUID>'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/rules/{rule_id}"
  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "ruleId": "ru_<UUID>",
  #   "rule": "<rule_content>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()["rule"]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")

  args = parser.parse_args()
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  rule_content = get_rule(session, args.rule_id)
  print(json.dumps(rule_content, indent=2))
