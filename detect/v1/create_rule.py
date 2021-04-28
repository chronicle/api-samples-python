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
"""Executable and reusable sample for creating a detection rule."""

import argparse

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_rule(http_session: requests.AuthorizedSession,
                rule_content: str) -> str:
  """Creates a new detection rule to find matches in logs.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_content: Content of the new detection rule, used to evaluate logs.

  Returns:
    Unique ID of the new detection rule ("ru_<UUID>").

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not rule_content:
    raise ValueError("Missing detection rule content.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/rules"
  body = {"rule": rule_content}

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "ruleId": "ru_<UUID>",
  #   "rule": "<rule_content>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()["ruleId"]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: create_rule.py -f <path>
      # STDIN example: cat rule.txt | create_rule.py -f -
      help="path of a file with the desired rule's content, or - for STDIN")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  new_rule_id = create_rule(session, args.rule_file.read())
  print(new_rule_id)
