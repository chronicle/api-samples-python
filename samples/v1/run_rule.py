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
"""Executable and reusable sample for running an existing detection rule."""

import argparse
import datetime
import re

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

RULE_ID_PATTERN = re.compile(r"ru_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
                             r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def run_rule(http_session: requests.AuthorizedSession, rule_id: str,
             event_start_time: datetime.datetime,
             event_end_time: datetime.datetime) -> str:
  """Starts running asynchronously a detection rule within a time range.

  The rule will run against all the *existing* logs that your organization has
  stored in Chronicle which have timestamps that fit within the specified time
  range.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to run ("ru_<UUID>").
    event_start_time: Lower bound of the time range for log processing by the
      specified rule. This function accepts a datetime object in any timezone
      (even timezone-unaware, i.e. local time) and converts it to UTC.
    event_end_time: Upper bound of the time range for log processing by the
      specified rule. This function accepts a datetime object in any timezone
      (even timezone-unaware, i.e. local time) and converts it to UTC.

  Returns:
    Unique ID of the requested asynchronous detection operation
      ("rulejob_jo_<UUID>").

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not RULE_ID_PATTERN.fullmatch(rule_id):
    raise ValueError(f"Invalid detection rule ID: '{rule_id}' != 'ru_<UUID>'.")
  if event_end_time < event_start_time:
    raise ValueError(
        f"End time '{event_end_time}' < start time '{event_start_time}'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/rules/{rule_id}:run"
  utc_start_datetime = event_start_time.astimezone(datetime.timezone.utc)
  utc_end_datetime = event_end_time.astimezone(datetime.timezone.utc)
  body = {
      "event_start_time": utc_start_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
      "event_end_time": utc_end_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "name": "operations/rulejob_jo_<UUID>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()["name"].split("/")[1]


def iso8601_datetime_local(local_date_time: str) -> datetime.datetime:
  """Converts an ISO 8601 string ("yyyy-mm-ddThh:mm:ss") to a datetime object.

  More details: https://en.wikipedia.org/wiki/ISO_8601

  Args:
    local_date_time: Date and time in the extended ("T") ISO 8601 format, but
      without a timezone, i.e. implicitly using whatever the local timezone is.

  Returns:
    Builtin timezone-unaware datetime object.

  Raises:
    ValueError: Invalid input value.
  """
  return datetime.datetime.strptime(local_date_time, "%Y-%m-%dT%H:%M:%S")


def iso8601_datetime_utc(utc_date_time: str) -> datetime.datetime:
  """Converts an ISO 8601 string ("yyyy-mm-ddThh:mm:ssZ") to a datetime object.

  More details: https://en.wikipedia.org/wiki/ISO_8601

  Args:
    utc_date_time: Date and time in the extended ("T") ISO 8601 format, where
      the time is in UTC ("Z").

  Returns:
    Builtin datetime object with a UTC timezone.

  Raises:
    ValueError: Invalid input value.
  """
  # Append the suffix "+0000" in order to produce a timezone-aware UTC datetime,
  # because strptime's "%z" does not recognize the meaning of the "Z" suffix.
  try:
    # Support (but don't require) sub-second parsing, but ignore anything
    # smaller than microseconds.
    utc_date_time = re.sub(r"(\d{6})\d+Z", r"\1Z", utc_date_time)
    return datetime.datetime.strptime(f"{utc_date_time}+0000",
                                      "%Y-%m-%dT%H:%M:%S.%fZ%z")
  except ValueError:
    # No microseconds? No problem, try to parse without them.
    # If there's a different parsing problem, it will surface below too.
    pass

  return datetime.datetime.strptime(f"{utc_date_time}+0000",
                                    "%Y-%m-%dT%H:%M:%SZ%z")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")
  parser.add_argument(
      "-tls",
      "--local_start_time",
      type=iso8601_datetime_local,
      help="Event start time in the local timezone ('yyyy-mm-ddThh:mm:ss')")
  parser.add_argument(
      "-tle",
      "--local_end_time",
      type=iso8601_datetime_local,
      help="Event end time in the local timezone ('yyyy-mm-ddThh:mm:ss')")
  parser.add_argument(
      "-tus",
      "--utc_start_time",
      type=iso8601_datetime_utc,
      help="Event start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-tue",
      "--utc_end_time",
      type=iso8601_datetime_utc,
      help="Event end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")

  args = parser.parse_args()
  if args.local_start_time and args.utc_start_time:
    raise ValueError("Use exactly one start time, local or UTC, not both.")
  if args.local_end_time and args.utc_end_time:
    raise ValueError("Use exactly one end time, local or UTC, not both.")
  if not (args.local_start_time or args.utc_start_time):
    raise ValueError("You must specify a start time, either local or UTC.")
  if not (args.local_end_time or args.utc_end_time):
    raise ValueError("You must specify an end time, either local or UTC.")
  start_time = args.local_start_time or args.utc_start_time
  end_time = args.local_end_time or args.utc_end_time

  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  operation_id = run_rule(session, args.rule_id, start_time, end_time)
  print(operation_id)
