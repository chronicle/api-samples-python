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
"""Executable and reusable sample for running a retrohunt."""

import argparse
import datetime
import pprint

from google.auth.transport import requests

from . import chronicle_auth

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def run_retrohunt(http_session: requests.AuthorizedSession, version_id: str,
                  start_time: datetime.datetime, end_time: datetime.datetime):
  """Run a retrohunt.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: Unique ID of the detection rule to run a retrohunt for
      ("ru_<UUID>" or "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version
      suffix isn't specified we use the rule's latest version.
    start_time: The start time of the time range the retrohunt will process.
    end_time: The end time of the time range the retrohunt will process.

  Returns:
    New retrohunt that was started for the given rule.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{version_id}:runRetrohunt"
  body = {
      "start_time": datetime_converter.strftime(start_time),
      "end_time": datetime_converter.strftime(end_time),
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "retrohuntId": "oh_<UUID>",
  #   "ruleId": "ru_<UUID>",
  #   "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #   "eventStartTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "eventEndTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "retrohuntStartTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "retrohuntEndTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "state": "RUNNING"/"DONE"/"CANCELLED",
  #   "progressPercentage": "<value from 0.0 to 1.0>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
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
      help="Retrohunt start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-et",
      "--end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="Retrohunt end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  rh = run_retrohunt(session, args.version_id, args.start_time, args.end_time)
  pprint.pprint(rh)
