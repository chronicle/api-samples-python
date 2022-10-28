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
"""Executable and reusable sample for listing lists."""

import argparse
import json
from typing import Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_lists(http_session: requests.AuthorizedSession,
               page_size: int = 0,
               page_token: str = "") -> Sequence[str]:
  """Retrieves a list of lists.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: Maximum number of lists to return. Must be non-negative, and is
      capped at a server-side limit of 1000. Optional - a server-side default of
      100 is used if the size is 0 or a None value.
    page_token: Page token from a previous ListReferenceLists call used for
      pagination. Optional - the first page is retrieved if the token is the
      empty string or a None value.

  Returns:
    List of lists and a page token for the next page of lists, if there are
    any.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/lists"
  params_list = [("page_size", page_size), ("page_token", page_token)]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  # Expected server response:
  # {
  #   "lists": [
  #     {
  #       "name": "<list_name>",
  #       "description": "<list_description>",
  #       "createTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #       "lines": [
  #         "rule_line",
  #         ...
  #       ],
  #       "contentType": "<content type. omitted if type is STRING list.>"
  #     },
  #     ...
  #   ],
  #   "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("lists", []), j.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of lists to return")
  parser.add_argument(
      "-t",
      "--page_token",
      type=str,
      required=False,
      help="page token from a previous ListReferenceLists call for pagination")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  lists, next_page_token = list_lists(session, args.page_size, args.page_token)
  print(json.dumps(lists, indent=2))
  print(f"Next page token: {next_page_token}")
