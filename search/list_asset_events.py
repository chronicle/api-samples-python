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
"""Executable and reusable sample for listing parsed asset events.

The events all reference a given asset in a given time range, and are returned
in UDM format.

API reference:
https://cloud.google.com/chronicle/docs/reference/search-api#listevents
https://cloud.google.com/chronicle/docs/unified-data-model/udm-usage
https://cloud.google.com/chronicle/docs/reference/udm-field-list
"""

import argparse
import datetime
import json
import sys
from typing import Any, Mapping, Optional, Sequence, Tuple

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
      "-n", "--hostname", type=str, required=False, help="asset hostname")
  parser.add_argument(
      "-i", "--ip_address", type=str, required=False, help="asset IP address")
  parser.add_argument(
      "-m", "--mac_address", type=str, required=False, help="asset MAC address")
  parser.add_argument(
      "-p",
      "--product_id",
      type=str,
      required=False,
      help="event ID from the product that generated the event")

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
      help="end of time range, also as an ISO 8601 string")
  parser.add_argument(
      "-tr",
      "--ref_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="reference time to disambiguate assets, also as an ISO 8601 string")
  parser.add_argument(
      "-tl",
      "--local_time",
      action="store_true",
      help=("time is specified in the system's local timezone (default = UTC)"))

  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of events to return (1-10,000, default = maximum)")

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)

  asset_indicators = (parsed_args.hostname, parsed_args.ip_address,
                      parsed_args.mac_address, parsed_args.product_id)
  if sum([1 for i in asset_indicators if i is not None]) != 1:
    print("Error: specify exactly one asset indicator")
    return None

  s, e, r = parsed_args.start_time, parsed_args.end_time, parsed_args.ref_time
  if parsed_args.local_time:
    s = s.replace(tzinfo=None).astimezone(datetime.timezone.utc)
    e = e.replace(tzinfo=None).astimezone(datetime.timezone.utc)
    r = r.replace(tzinfo=None).astimezone(datetime.timezone.utc)
  if s > datetime.datetime.utcnow().astimezone(datetime.timezone.utc):
    print("Error: start time should not be in the future")
    return None
  if r > datetime.datetime.utcnow().astimezone(datetime.timezone.utc):
    print("Error: reference time should not be in the future")
    return None
  if s >= e:
    print("Error: start time should not be same as or later than the end time")
    return None

  ps = parsed_args.page_size or 0
  if ps < 0 or ps > 10000:
    print("Error: page size valid range is 0-10,000 (0 = default = maximum)")
    return None

  return parsed_args


def list_asset_events(
    http_session: requests.AuthorizedSession,
    indicator: str,
    asset: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    ref_time: datetime.datetime,
    page_size: Optional[int] = 0
) -> Tuple[Sequence[Mapping[str, Any]], str, bool]:
  """Lists up to 10,000 UDM events that reference an asset in a time range.

  If there are more matching events than what was returned (according to the
  second element in the tuple returned by this function), you should split this
  call into multiple shorter time ranges to ensure you have visibility into all
  the available events.

  Args:
    http_session: Authorized session for HTTP requests.
    indicator: Type of asset indicator - either "hostname", "asset_ip_address",
      "mac", or "product_id".
    asset: Asset indicator value - a specific hostname, IP address, MAC address,
      or event ID from the logging product that generated the event.
    start_time: Inclusive beginning of the time range of events to return, with
      any timezone (even a timezone-unaware datetime object, i.e. local time).
    end_time: The exclusive end of the time range of events to return, with any
      timezone (even a timezone-unaware datetime object, i.e. local time).
    ref_time: Reference time, used to disambiguate asset indicators, which may
      refer to different assets at different points in time, with any timezone
      (even a timezone-unaware datetime object, i.e. local time).
    page_size: Maximum number of events to return, up to 10,000 (default =
      10,000).

  Returns:
    Tuple with 3 elements: (1) a list of all the UDM events (within the defined
    page) as Python dictionaries, (2) a Boolean value indicating whether there
    are matching events that were not returned, i.e. whether the matching event
    count exceeded the page size, and (3) a URL to see all these asset events in
    the Chronicle web UI.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
    (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/asset/listevents"
  params = {
      "asset." + indicator: asset,
      "start_time": datetime_converter.strftime(start_time),
      "end_time": datetime_converter.strftime(end_time),
      "reference_time": datetime_converter.strftime(ref_time),
      "page_size": page_size,
  }
  response = http_session.request("GET", url, params=params)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  d = response.json()
  return d.get("events", []), d.get("moreDataAvailable", False), d["uri"][0]


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  start, end, ref = cli.start_time, cli.end_time, cli.ref_time
  if cli.local_time:
    start = start.replace(tzinfo=None)
    end = end.replace(tzinfo=None)
    ref = ref.replace(tzinfo=None)

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  common_args = (start, end, ref, cli.page_size)
  if cli.hostname:
    events, is_more, web_url = list_asset_events(session, "hostname",
                                                 cli.hostname, *common_args)
  elif cli.ip_address:
    events, is_more, web_url = list_asset_events(session, "asset_ip_address",
                                                 cli.ip_address, *common_args)
  elif cli.mac_address:
    events, is_more, web_url = list_asset_events(session, "mac_address",
                                                 cli.mac_address, *common_args)
  else:
    events, is_more, web_url = list_asset_events(session, "product_id",
                                                 cli.product_id, *common_args)
  print(json.dumps(events, indent=2))
  print(f"\nMore events? {is_more}")
  print(f"\nChronicle asset view URL: {web_url}")
