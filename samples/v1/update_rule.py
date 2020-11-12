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
"""Executable and reusable sample for updating a detection rule."""

import argparse
import re

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

RULE_ID_PATTERN = re.compile(r"ru_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
                             r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def update_rule(http_session: requests.AuthorizedSession, existing_rule_id: str,
                new_rule_content: str):
  """Modifies the content of an existing detection rule.

  Args:
    http_session: Authorized session for HTTP requests.
    existing_rule_id: Unique ID of an existing detection rule ("ru_<UUID>").
    new_rule_content: New content for that detection rule.

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not RULE_ID_PATTERN.fullmatch(existing_rule_id):
    raise ValueError(
        f"Invalid detection rule ID: '{existing_rule_id}' != 'ru_<UUID>'.")
  if not new_rule_content:
    raise ValueError("Missing detection rule content.")

  url = (f"{CHRONICLE_API_BASE_URL}/v1/rules/{existing_rule_id}" +
         "?update_mask.paths=rule.rule")
  body = {"rule": new_rule_content}

  response = http_session.request("PATCH", url, json=body)
  # Expected server response:
  # {
  #   "ruleId": "ru_<UUID>",
  #   "rule": "<rule_content>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: create_rule.py -f <path>
      # STDIN example: cat rule.txt | create_rule.py -
      help="path of a file with the desired rule's content, or - for STDIN")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  update_rule(session, args.rule_id, args.rule_file.read())
