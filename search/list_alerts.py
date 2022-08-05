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
https://cloud.google.com/chronicle/docs/reference/search-api#listalerts
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
      "-te",
      "--end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help=("end of time range, as an ISO 8601 string ('yyyy-mm-ddThh:mm:ss')"))
  parser.add_argument(
      "-tl",
      "--local_time",
      action="store_true",
      help=("times are specified in the system's local timezone " +
            "(default = UTC)"))
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      default=100000,
      help=("Maximum number of alerts to return, up to 100,000" +
            "(default = 100,000)"))

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)
  s, e, ps = parsed_args.start_time, parsed_args.end_time, parsed_args.page_size
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
  if ps > 100000 or ps < 1:
    print("Error: page size can not be more than 100,000 or less than 1")
    return None

  return parsed_args


def list_alerts(
    http_session: requests.AuthorizedSession,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    page_size: Optional[int] = 100000) -> Mapping[str, Sequence[Any]]:
  """Lists up to 100,000 asset- and user-based alerts in the given time range.

  If you receive the maximum number of results, there might still be more
  discovered within the specified time range. You might want to narrow the time
  range and issue the call again to ensure you have visibility on the results.

  Args:
    http_session: Authorized session for HTTP requests.
    start_time: The inclusive beginning of the time range of alerts to return,
      with any timezone (even a timezone-unaware datetime object, i.e. local
      time).
    end_time: The exclusive end of the time range of alerts to return, with any
      timezone (even a timezone-unaware datetime object, i.e. local time).
    page_size: Maximum number of alerts to return, up to 100,000 (default =
      100,000).

  Returns:
    {
      "alerts": [
        ...One or more asset alerts (if zero, no "alerts" field at all)...
      ],
      "userAlerts": [
        ...One or more user alerts (if zero, no "userAlerts" field at all)...
      ]
    }

  Asset alert structure:
    {
      "asset": {
        "hostname": "..." <-- Or IP address, MAC address, product ID
      },
      "alertInfos": [
        ...One or more alert infos...
      ]
    }

  User alert structure:
    {
      "user": {
        "email": "..." <-- Or user name, Windows SID, employee ID, LDAP ID
      },
      "alertInfos": [
        ...One or more alert infos...
      ]
    }

  Alert info structure:
    {
      "name": "...",
      "sourceProduct": "...",
      "timestamp": "yyyy-mm-ddThh:mm:ssZ",
      "rawLog": "...", <-- Base64 encoded
      "uri": [
        "https://customer.backstory.chronicle.security/..."
      ],
      "udmEvent": {
        ...
      }
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
    (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/alert/listalerts"
  params = {
      "start_time": datetime_converter.strftime(start_time),
      "end_time": datetime_converter.strftime(end_time),
      "page_size": page_size
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

  start, end, size = cli.start_time, cli.end_time, cli.page_size
  if cli.local_time:
    start, end = start.replace(tzinfo=None), end.replace(tzinfo=None)

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(json.dumps(list_alerts(session, start, end, size), indent=2))
