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
"""Executable and reusable sample for listing retrohunts.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#listretrohunts
"""

import argparse
import json
from typing import Any, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_retrohunts(
    http_session: requests.AuthorizedSession,
    version_id: str,
    retrohunt_state: str = "",
    page_size: int = 0,
    page_token: str = "") -> Tuple[Sequence[Mapping[str, Any]], str]:
  """Lists retrohunts.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: Unique ID of the detection rule to list retrohunts for.
      Valid version ID formats:
        Retrohunts for a specific rule version:
        "ru_<UUID>@v_<seconds>_<nanoseconds>"
        Retrohunts for the latest version of a rule: "ru_<UUID>"
        Retrohunts across all versions of a rule: "ru_<UUID>@-"
        Retrohunts across all rules and all versions: "-"
    retrohunt_state: The status of the retrohunt to filter by (i.e. 'RUNNING')
      (default = no filter on retrohunt state).
      Optional - retrohunts of all states are returned.
    page_size: Maximum number of retrohunts to return.
      Must be non-negative, and is capped at a server-side limit of 1000.
      Optional - a server-side default of 100 is used if the size is 0 or a
      None value.
    page_token: Page token from a previous ListRetrohunts call used for
      pagination.
      Optional - the first page is retrieved if the token is the
      empty string or a None value.

  Returns:
    All the retrohunts (within the defined page) ordered by descending
    retrohunt start time, as well as a Base64 token for getting the retrohunts
    of the next page (any empty token string means the currently retrieved page
    is the last one).

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{version_id}/retrohunts"
  params_list = [("state", retrohunt_state),
                 ("page_size", page_size), ("page_token", page_token)]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  # Expected server response:
  # {
  #     "retrohunts": [
  #         {
  #             "retrohuntId": "oh_<UUID>",
  #             "ruleId": "ru_<UUID>",
  #             "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #             "eventStartTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #             "eventEndTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #             "retrohuntStartTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #             "retrohuntEndTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #             "state": "RUNNING"/"DONE"/"CANCELLED",
  #             "progressPercentage": "<value from 0.00 to 100.00>"
  #         },
  #         ...
  #     ]
  #     "nextPageToken": "<next_page_token>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  j = response.json()
  return j.get("retrohunts", []), j.get("nextPageToken", "")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-vi",
      "--version_id",
      type=str,
      required=True,
      help="version ID of the rule to list retrohunts for ('- | ru_<UUID>@- | ru_<UUID>[@v_<seconds>_<nanoseconds>]')"
  )
  parser.add_argument(
      "-st",
      "--retrohunt_state",
      type=str,
      required=False,
      help="retrohunt state (i.e. 'RUNNING', 'DONE', 'CANCELLED')")
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of retrohunts to return")
  parser.add_argument(
      "-t",
      "--page_token",
      type=str,
      required=False,
      help="page token from a previous ListRetrohunts call used for pagination")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  retrohunts, next_page_token = list_retrohunts(session, args.version_id,
                                                args.retrohunt_state,
                                                args.page_size, args.page_token)
  print(json.dumps(retrohunts, indent=2))
  print(f"Next page token: {next_page_token}")
