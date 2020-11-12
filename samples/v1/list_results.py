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
"""Executable and reusable sample for enumerating all the detection results."""

import argparse
import base64
import binascii
import pprint
import re
from typing import Any, Mapping, Optional, Sequence, Tuple

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

OPERATION_ID_PATTERN = re.compile(
    r"rulejob_jo_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
    r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")

DECODED_TOKEN_PATTERN = re.compile(
    rb"[\s\S]+[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
    rb"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def list_results(
    http_session: requests.AuthorizedSession,
    operation_id: str,
    page_size: int = 0,
    page_token: Optional[str] = None
) -> Tuple[Sequence[Mapping[str, Any]], str]:
  """Retrieves all the results of the specified detection operation.

  This includes both errors and Universal Data Model (UDM) matches. Any results
  that are fetched before the operation has completed may be incomplete and
  should not be considered authoritative.

  Args:
    http_session: Authorized session for HTTP requests.
    operation_id: Unique ID of the asynchronous detection operation
      ("rulejob_jo_<UUID>").
    page_size: Maximum number of results in the response. Must be non-negative.
      Optional - no client-side limit by default.
    page_token: Base64-encoded string token to retrieve a specific page of
      results. Optional - we retrieve the first page if the token is an empty
      string or a None value.

  Returns:
    All the results (within the defined page) as an ordered sequence of errors
    or UDM matches, as well as a Base64 token for getting the results of the
    next page (an empty token string means the currently retrieved page is the
    last one).

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if page_size < 0:
    raise ValueError(f"Invalid input: page_size = {page_size}, must be >= 0.")
  if page_token:
    try:
      if not DECODED_TOKEN_PATTERN.fullmatch(base64.b64decode(page_token)):
        raise ValueError(f"Invalid page token: '{page_token}'.")
    except binascii.Error:
      raise ValueError(f"Invalid page token: '{page_token}'.")

  url = (f"{CHRONICLE_API_BASE_URL}/v1/rules_results?name=operations/" +
         operation_id)
  if page_size > 0:
    url += f"&page_size={page_size}"
  if page_token:
    url += f"&page_token={page_token}"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "nextPageToken": "<base64>",
  #   "results": [
  #     {
  #       "match": {<UDM keys and values / sub-dictionaries>...}
  #     },
  #     ...
  #     {
  #       "error": {"errorMessage": "..."}
  #     },
  #     ...
  #   ]
  # }
  # - or -
  # { }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  json = response.json()
  return json.get("results", []), json.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-oi",
      "--operation_id",
      type=str,
      required=True,
      help="detection operation ID ('rulejob_jo_<UUID>')")
  parser.add_argument(
      "-ps",
      "--page_size",
      type=int,
      default=0,
      help="maximum number of results to return (default: 0 = no limit)")
  parser.add_argument(
      "-pt",
      "--page_token",
      type=str,
      default=None,
      help="page token (default: none)")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  results, next_page_token = list_results(session, args.operation_id,
                                          args.page_size, args.page_token)
  pprint.pprint(results)
  print(f"Next page token: {next_page_token}")
