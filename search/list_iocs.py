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
"""Executable and reusable sample for listing Indications of Compromise.

API reference:
https://cloud.google.com/chronicle/docs/reference/search-api#listiocs
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
      "-ts",
      "--start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help=("beginning of time range, as an ISO 8601 string " +
            "('yyyy-mm-ddThh:mm:ss')"))
  parser.add_argument(
      "-tl",
      "--local_time",
      action="store_true",
      help=("time is specified in the system's local timezone (default = UTC)"))
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      default=10000,
      help=("Maximum number of IoCs to return, up to 10,000" +
            "(default = 10,000)"))

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)
  s, ps = parsed_args.start_time, parsed_args.page_size
  if parsed_args.local_time:
    s = s.replace(tzinfo=None).astimezone(datetime.timezone.utc)
  if s > datetime.datetime.now().astimezone(datetime.timezone.utc):
    print("Error: start time should not be in the future")
    return None
  if ps > 10000 or ps < 1:
    print("Error: page size can not be more than 10,000 or less than 1")
    return None

  return parsed_args


def list_iocs(http_session: requests.AuthorizedSession,
              start_time: datetime.datetime,
              page_size: Optional[int] = 10000) -> Mapping[str, Any]:
  """Lists up to 10,000 Indications of Compromise (IoCs) after the start time.

  If you receive the maximum number of results, there might still be more
  discovered within the specified time range. You might want to narrow the time
  range and issue the call again to ensure you have visibility on the results.

  You can use the API call ListArtifactAssets to drill-down on the assets
  associated with this IoC (hostnames, IP and MAC addresses).

  Args:
    http_session: Authorized session for HTTP requests.
    start_time: Inclusive beginning of the time range of IoCs to return, with
      any timezone (even a timezone-unaware datetime object, i.e. local time).
    page_size: Maximum number of IoCs to return, up to 10,000 (default =
      10,000).

  Returns:
    {
      "response": {
        "matches": [
          {
            "artifact": {
              "domainName": "..." <-- Or destination IP address, or file hashes
            },
            "sources": [
              {
                "source": "..."
                "confidenceScore": {
                  "normalizedConfidenceScore": "..." <-- e.g. low/medium/high
                  "intRawConfidenceScore": 0,
                },
                "rawSeverity": "...",
                "category": "...",
              }
            ],
            "iocIngestTime": "yyyy-mm-ddThh:mm:ssZ",
            "firstSeenTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
            "lastSeenTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
            "uri": [
              "https://customer.backstory.chronicle.security/..."
            ]
          },
          ...More matches...
        ]
      }
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
    (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/ioc/listiocs"
  s = datetime_converter.strftime(start_time)
  params = {"start_time": s, "page_size": page_size}
  response = http_session.request("GET", url, params=params)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  start, size = cli.start_time, cli.page_size
  if cli.local_time:
    start = start.replace(tzinfo=None)

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(json.dumps(list_iocs(session, start, size), indent=2))
