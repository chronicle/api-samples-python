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
"""Executable and reusable sample for running a rule and waiting for it.

This module demonstrates combining multiple single-purpose modules into a larger
workflow.
"""

import argparse
import datetime
import pprint
import time
from typing import Any, Mapping, Sequence

from . import cancel_operation
from . import chronicle_auth
from . import get_operation
from . import list_results
from . import run_rule
from google.auth.transport import requests

DEFAULT_SLEEP_SECONDS = 5
DEFAULT_TIMEOUT_MINUTES = 1440.0  # 1 day = 60 * 24 = 1440 minutes.


def run_rule_and_wait(
    http_session: requests.AuthorizedSession,
    rule_id: str,
    event_start_time: datetime.datetime,
    event_end_time: datetime.datetime,
    sleep_seconds: int = DEFAULT_SLEEP_SECONDS,
    timeout_minutes: float = DEFAULT_TIMEOUT_MINUTES
) -> Sequence[Mapping[str, Any]]:
  """Runs a detection rule within a time range, and waits for the results.

  The rule will run against all the logs that your organization has stored in
  Chronicle which have timestamps that fit within the specified time range, it
  will not evaluate new incoming logs (i.e. this is not a "live rule").

  You may set a timeout for this polling loop, in which case the operation will
  be automatically cancelled if it exceeds this timeout.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to run ("ru_<UUID>").
    event_start_time: Lower bound of the time range for log processing by the
      specified rule. This function accepts a datetime object in any timezone
      (even timezone-unaware, i.e. local time) and converts it to UTC.
    event_end_time: Upper bound of the time range for log processing by the
      specified rule. This function accepts a datetime object in any timezone
      (even timezone-unaware, i.e. local time) and converts it to UTC.
    sleep_seconds: Optional interval between operation checks, until it's done.
    timeout_minutes: Optional timeout in minutes (e.g. 76.5 = 1 hour, 16 minutes
      and 30 seconds, default = 1 day).

  Returns:
    All the results as an ordered sequence of errors or UDM matches.

  Raises:
    ValueError: Invalid input value.
    TimeoutError: Detection rule not completed after the specified timeout.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  deadline = datetime.datetime.now() + datetime.timedelta(
      minutes=timeout_minutes)

  operation_id = run_rule.run_rule(http_session, rule_id, event_start_time,
                                   event_end_time)

  operation = get_operation.Operation({
      "name": "/",
      "metadata": {
          "ruleId": "",
          "@type": "",
      },
      "done": False,
  })
  while datetime.datetime.now() < deadline and not operation.is_done:
    print(f"[{time.asctime()}] Waiting for the operation to complete...")
    time.sleep(sleep_seconds)
    operation = get_operation.get_operation(http_session, operation_id)

  if datetime.datetime.now() >= deadline:
    cancel_operation.cancel_operation(http_session, operation_id)
    raise TimeoutError(
        f"Detection rule not completed after {timeout_minutes} minutes.")

  all_results = []
  page_token = None
  next_page_token = "dummy_initial_value"
  while next_page_token:
    page_results, next_page_token = list_results.list_results(
        http_session, operation.id, page_token=page_token)
    all_results.extend(page_results)
    page_token = next_page_token
  return all_results


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")
  parser.add_argument(
      "-tls",
      "--local_start_time",
      type=run_rule.iso8601_datetime_local,
      help="Event start time in the local timezone ('yyyy-mm-ddThh:mm:ss')")
  parser.add_argument(
      "-tle",
      "--local_end_time",
      type=run_rule.iso8601_datetime_local,
      help="Event end time in the local timezone ('yyyy-mm-ddThh:mm:ss')")
  parser.add_argument(
      "-tus",
      "--utc_start_time",
      type=run_rule.iso8601_datetime_utc,
      help="Event start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-tue",
      "--utc_end_time",
      type=run_rule.iso8601_datetime_utc,
      help="Event end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-ss",
      "--sleep_seconds",
      type=int,
      default=DEFAULT_SLEEP_SECONDS,
      help="interval between operation polls in seconds (default = 5)")
  parser.add_argument(
      "-tm",
      "--timeout_minutes",
      type=float,
      default=DEFAULT_TIMEOUT_MINUTES,
      help="timeout in minutes (default = 1 day)")

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
  results = run_rule_and_wait(session, args.rule_id, start_time, end_time,
                              args.sleep_seconds, args.timeout_minutes)
  pprint.pprint(results)
