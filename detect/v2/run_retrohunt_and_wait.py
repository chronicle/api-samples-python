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
"""Executable and reusable sample for running a retrohunt and waiting for it.

This module demonstrates combining multiple single-purpose modules into a larger
workflow.
"""

import argparse
import datetime
import json
import time
from typing import Any, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter
from common import regions
from . import cancel_retrohunt
from . import get_retrohunt
from . import list_detections
from . import run_retrohunt

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

# Sleep duration used to wait until next retrohunt status check.
DEFAULT_SLEEP_SECONDS = 5
# Timeout used to wait until retrohunt is complete.
DEFAULT_TIMEOUT_MINUTES = 1440.0  # 1 day = 60 * 24 = 1440 minutes.


def get_retrohunt_info(
    retrohunt: Mapping[str, Any]) -> Tuple[str, str, str, float]:
  """Helper function to extract versionId, retrohuntId, state, and progressPercentage from retrohunt.

  Args:
    retrohunt: Retrohunt in a Mapping format.
  Returns:
    versionId, retrohuntId, state, progressPercentage.
  """
  return (retrohunt.get("versionId", ""), retrohunt.get("retrohuntId", ""),
          retrohunt.get("state", "STATE_UNSPECIFIED"),
          retrohunt.get("progressPercentage", 0.0))


def run_retrohunt_and_wait(
    http_session: requests.AuthorizedSession,
    version_id: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
    sleep_seconds: int = DEFAULT_SLEEP_SECONDS,
    timeout_minutes: float = DEFAULT_TIMEOUT_MINUTES,
    page_size: int = 0
    ) -> Tuple[Sequence[Mapping[str, Any]], str]:
  """Runs a retrohunt and wait, and receive detections.

  When retrohunt does not complete within the 'timeout_minutes' time period,
  it cancels the retrohunt and returns TimeoutError.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: Unique ID of the detection rule to retrieve errors for
      ("ru_<UUID>" or "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version
      suffix isn't specified we use the rule's latest version.
    start_time: The start time of the time range the retrohunt will process.
    end_time: The end time of the time range the retrohunt will process.
    sleep_seconds: Optional interval between retrohunt status checks, until it's
      DONE or CANCELLED.
    timeout_minutes: Optional timeout in minutes. This is used to wait for the
      retrohunt to complete.
    page_size: Maximum number of detections in the response. Must be
      non-negative. This is optional. If not provided, default value 100 is
      applied.

  Returns:
    First page of detections and page token, which is a Base64 token for
    getting the detections of the next page (an empty token string means the
    currently retrieved page is the last one).

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
    TimeoutError: When retrohunt does not complete by timeout.
  """
  deadline = datetime.datetime.now() + datetime.timedelta(
      minutes=timeout_minutes)
  # Start RunRetrohunt by calling RunRetrohunt.
  retrohunt_rep = run_retrohunt.run_retrohunt(http_session, version_id,
                                              start_time, end_time)
  version_id, retrohunt_id, state, progress_percentage = get_retrohunt_info(
      retrohunt_rep)
  print(f"Retrohunt started. retrohunt_id: {retrohunt_id}")
  now = datetime.datetime.now()
  while now < deadline and state not in ("DONE", "CANCELLED"):
    print((f"Waiting for retrohunt to complete. Retrohunt is running at "
           f"{progress_percentage}% .."))
    time.sleep(sleep_seconds)
    retrohunt_rep = get_retrohunt.get_retrohunt(http_session,
                                                version_id,
                                                retrohunt_id)
    version_id, retrohunt_id, state, progress_percentage = get_retrohunt_info(
        retrohunt_rep)
    now = datetime.datetime.now()

  # We finished waiting for the retrohunt to complete. We cancel the retrohunt
  # if it is still running.
  if state == "RUNNING":
    print((f"Retrohunt did not complete. "
           f"Cancelling retrohunt for versionID: {version_id}"))
    # When cancel_retrohunt fails, it raises error and stop the script here.
    cancel_retrohunt.cancel_retrohunt(http_session, version_id,
                                      retrohunt_id)
    raise TimeoutError(
        f"Retrohunt not completed after {timeout_minutes} minutes.")

  print("Returning first page of detections.")
  return list_detections.list_detections(
      http_session,
      version_id=version_id,
      page_size=page_size,
      start_time=start_time,
      end_time=end_time)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-vi",
      "--version_id",
      type=str,
      required=True,
      help="version ID ('ru_<UUID>[@v_<seconds>_<nanoseconds>]')")
  parser.add_argument(
      "-st",
      "--start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="Event start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-et",
      "--end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="Event end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-ss",
      "--sleep_seconds",
      type=int,
      default=DEFAULT_SLEEP_SECONDS,
      help="interval between retrohunt status polls in seconds (default = 5)")
  parser.add_argument(
      "-tm",
      "--timeout_minutes",
      type=float,
      default=DEFAULT_TIMEOUT_MINUTES,
      help=("timeout in minutes (default = 1 day) used to wait for retrohunt"
            "to complete and return detections"))
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of detections to return")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  detections, next_page_token = run_retrohunt_and_wait(
      session, args.version_id, args.start_time, args.end_time,
      args.sleep_seconds, args.timeout_minutes, args.page_size)
  print(json.dumps(detections, indent=2))
  print(f"Next page token: {next_page_token}")
