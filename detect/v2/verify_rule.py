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
"""Executable and reusable sample for verifying a detection rule.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#verifyrule
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def verify_rule(http_session: requests.AuthorizedSession,
                rule_content: str) -> Mapping[str, Any]:
  """Validates that a detection rule is a valid YL2 rule.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_content: Content of the detection rule.

  Returns:
    A compilation error if there is one.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules:verifyRule"
  body = {"rule_text": rule_content}

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "compilationError": "<error_message>", <-- IFF compilation failed.
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: python3 verify_rule.py -f <path>
      # STDIN example: cat rule.txt | python3 verify_rule.py -f -
      help="path of a file with the rule's content, or - for STDIN")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  resp = verify_rule(session, args.rule_file.read())
  print(json.dumps(resp, indent=2))
