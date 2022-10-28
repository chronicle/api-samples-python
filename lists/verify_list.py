#!/usr/bin/env python3
# Copyright 2022 Google LLC
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
"""Executable and reusable sample for creating a list."""

import argparse
from typing import Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def verify_list(http_session: requests.AuthorizedSession,
                content_lines: Sequence[str], content_type: str):
  """Verifies a list.

  Args:
    http_session: Authorized session for HTTP requests.
    content_lines: Array containing each line of the list's content.
    content_type: Type of list content, indicating how to interpret this list.

  Returns:
    None

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/lists:verifyReferenceList"
  body = {
      "lines": content_lines,
      "content_type": content_type,
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # { "success": true }
  #
  # or
  #
  # {
  #   "errors": [
  #     {
  #       "lineNumber": <number>,
  #       "errorMessage": "<error message>"
  #     }
  #   ]
  # }

  if response.ok:
    # Verification request succeeded. Response contents indicates whether or not
    # the list is valid.
    if response.json().get("success"):
      print("List content is valid.")
    else:
      print("List content is invalid. Errors below.")
      for e in response.json().get("errors"):
        print(e)

  if response.status_code >= 400:
    # There was an error performing the verification.
    print(response.text)
  response.raise_for_status()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-t",
      "--content_type",
      type=str,
      default="CONTENT_TYPE_DEFAULT_STRING",
      help="type of list lines")
  parser.add_argument(
      "-f",
      "--list_file",
      type=argparse.FileType("r"),
      required=True,
      # File example:
      #   python3 -m lists.verify_list <other args> -f <path>
      # STDIN example:
      #   cat <path> | python3 -m lists.verify_list <other args> -f -
      help="path of a file containing the list content, or - for STDIN")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  verify_list(
      session,
      args.list_file.read().splitlines(),
      args.content_type,
  )
