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
"""Executable and reusable sample for listing asset- and user-based alerts.

API reference:
https://cloud.devsite.corp.google.com/chronicle/docs/reference/uppercase-api#listalerts
"""

import argparse
import json
import sys
from typing import Optional, Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help=("maximum number of alerts to return"))
  parser.add_argument(
      "-t",
      "--page_token",
      type=str,
      required=False,
      help=("page token from a previous ListAlerts call used for pagination"))

  parsed_args = parser.parse_args(args)
  return parsed_args


def list_alerts(http_session: requests.AuthorizedSession,
                page_size: Optional[int] = 100,
                page_token: str = "") -> Sequence[str]:
  """Lists up to 100 Uppercase alerts.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: Maximum number of rules to return. Must be non-negative. Optional
    - a server-side default of 100 is used if the size is 0 or a None value.
    page_token: Page token from a previous ListAlerts call used for pagination.
      Optional - the first page is retrieved if the token is the empty string or
      a None value.

  Returns:
    List of Uppercase alerts and a page token for the next page of alerts, only
    populated if there are more to fetch.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
    (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/uppercaseAlerts"
  params = {"page_token": page_token, "page_size": page_size}
  response = http_session.request("GET", url, params=params)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("uppercaseAlerts", []), j.get("nextPageToken", "")


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  token, size = cli.page_token, cli.page_size

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  uppercase_alerts, next_page_token = list_alerts(session, size, token)
  print(json.dumps(uppercase_alerts, indent=2))
  print(f"Next page token: {next_page_token}")
