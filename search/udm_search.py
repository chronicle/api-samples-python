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
"""Executable and reusable sample for UDM Search.

API reference:
https://cloud.google.com/chronicle/docs/reference/search-api#udmsearch
"""

import argparse
import datetime
import json
import sys
from typing import Any, Mapping, Optional, Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-q", "--query", type=str, required=True, help=("UDM Search query"))
  parser.add_argument(
      "-ts",
      "--start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help=(
          "start of time range, as an ISO 8601 string ('yyyy-mm-ddThh:mm:ss')"))
  parser.add_argument(
      "-te",
      "--end_time",
      required=True,
      type=datetime_converter.iso8601_datetime_utc,
      help=("end of time range, as an ISO 8601 string ('yyyy-mm-ddThh:mm:ss')"))
  parser.add_argument(
      "-tl",
      "--local_time",
      action="store_true",
      help=("time is specified in the system's local timezone (default = UTC)"))
  parser.add_argument(
      "-l",
      "--limit",
      type=int,
      default=1000,
      help=("Limit on the maximum number of matches to return, up to 1,000" +
            "(default = 1,000)"))

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)
  s, e, limit = parsed_args.start_time, parsed_args.end_time, parsed_args.limit
  if parsed_args.local_time:
    s = s.replace(tzinfo=None).astimezone(datetime.timezone.utc)
    e = e.replace(tzinfo=None).astimezone(datetime.timezone.utc)
  if s > datetime.datetime.now().astimezone(datetime.timezone.utc):
    print("Error: start time should not be in the future")
    return None
  if e > datetime.datetime.now().astimezone(datetime.timezone.utc):
    print("Error: end time should not be in the future")
    return None
  if s >= e:
    print("Error: start time should not be same as or later than end time")
    return None
  if limit > 1000 or limit < 1:
    print("Error: limit can not be more than 1,000 or less than 1")
    return None

  return parsed_args


def udm_search(http_session: requests.AuthorizedSession,
               query: str,
               start_time: datetime.datetime,
               end_time: datetime.datetime,
               limit: Optional[int] = 1000) -> Mapping[str, Any]:
  """Performs a UDM search across the specified time range.

  Args:
    http_session: Authorized session for HTTP requests.
    query: UDM search query.
    start_time: Inclusive beginning of the time range to search, with any
      timezone (even a timezone-unaware datetime object, i.e. local time).
    end_time: Exclusive end of the time range to search, with any timezone (even
      a timezone-unaware datetime object, i.e. local time).
    limit: Maximum number of matched events to return, up to 1,000 (default =
      1,000).

  Returns:
    {
      "events": [
        {
          "name": "...",
          "udm": {
            "metadata": { ... },
            "principal": { ... },
            "target": { ... },
          },
        },
        {
          "name": "...",
          "udm": {
            "metadata": { ... },
            "principal": { ... },
            "target": { ... },
          },
        },
        ...More matched events...
      ]
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
    (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/events:udmSearch"
  s = datetime_converter.strftime(start_time)
  e = datetime_converter.strftime(end_time)
  params = {
      "query": query,
      "time_range.start_time": s,
      "time_range.end_time": e,
      "limit": limit
  }
  response = http_session.request("GET", url, params=params)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  q, start, end, l = cli.query, cli.start_time, cli.end_time, cli.limit
  if cli.local_time:
    start = start.replace(tzinfo=None)

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(json.dumps(udm_search(session, q, start, end, l), indent=2))
