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
"""Executable and reusable sample for polling a detection operation."""

import argparse
import datetime
import re
from typing import Optional

import dataclasses
from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

OPERATION_ID_PATTERN = re.compile(
    r"rulejob_jo_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
    r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


@dataclasses.dataclass
class Operation:
  """Container for the details and the latest status of an operation.

  The purpose of this class is to ensure that users don't have to do any parsing
  of operation data, and don't have to be aware of implicit relations between
  fields in the raw JSON data (e.g. the existence of key "X" depends on the
  value of key "Y").
  """
  id: str

  rule_id: str
  rule_metadata_type: str
  event_start_time: Optional[datetime.datetime]
  event_end_time: Optional[datetime.datetime]

  run_start_time: datetime.datetime
  run_end_time: Optional[datetime.datetime]

  # False = in progress, True = finished, with either errors or results.
  is_done: bool

  # 0  = OK (no error)
  # 1  = cancelled (typically by the caller)
  # 3  = invalid argument
  # 4  = deadline exceeded
  # 8  = resource exhausted
  # 10 = aborted (the client should retry at a higher level, e.g. when a
  #      client-specified test-and-set fails, indicating the client should
  #      restart a read-modify-write sequence)
  # 14 = unavailable (most likely a transient condition, which can be corrected
  #      by retrying the failing call with a backoff)
  # 11 = out of range
  # 12 = not implemented
  # 13 = internal error
  error_code: Optional[int]
  error_message: Optional[str]

  def __init__(self, json):
    """Constructs an Operation object from the given JSON dictionary."""
    metadata = json["metadata"]
    times = (
        metadata.get("eventStartTime"),
        metadata.get("eventEndTime"),
        metadata.get("runStartedTime"),
        metadata.get("runCompletedTime"),
    )
    self.id = json["name"].split("/")[1]
    self.rule_id = metadata["ruleId"]
    self.rule_metadata_type = metadata["@type"]
    self.event_start_time = iso8601_datetime_utc(times[0]) if times[0] else None
    self.event_end_time = iso8601_datetime_utc(times[1]) if times[1] else None
    self.run_start_time = iso8601_datetime_utc(times[2]) if times[2] else None
    self.run_end_time = iso8601_datetime_utc(times[3]) if times[3] else None
    self.is_done = json.get("done", False)
    self.error_code = json.get("error", {}).get("code")
    self.error_message = json.get("error", {}).get("message")


def get_operation(http_session: requests.AuthorizedSession,
                  operation_id: str) -> Operation:
  """Retrieves the details and latest state of a specific detection operation.

  Args:
    http_session: Authorized session for HTTP requests.
    operation_id: Unique ID of the asynchronous detection operation to poll
      ("rulejob_jo_<UUID>").

  Returns:
    Data container for the details and the state of the specified operation.

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not OPERATION_ID_PATTERN.fullmatch(operation_id):
    raise ValueError(f"Invalid detection operation ID: '{operation_id}' != " +
                     "'rulejob_jo_<UUID>'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/operations/{operation_id}"
  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "name": "operations/rulejob_jo_<UUID>",
  #   "metadata": {
  #     "@type": "type.googleapis.com/chronicle.backstory.v1.RunRuleMetadata"
  #              (or "...v1.EnableLiveRuleMetadata"),
  #     "ruleId": "ru_<UUID>",
  #     "eventStartTime": "yyyy-mm-ddThh:mm:ssZ",  <-- Not set in live rules.
  #     "eventEndTime": "yyyy-mm-ddThh:mm:ssZ"  <-- Not set in live rules.
  #   },
  #   "done": true,  <-- IFF execution is finished, or operation is cancelled.
  #   "error": {"code": <int>, "message": <str>}  <-- IFF there is an error.
  #   "response": {  <-- IFF "done" is true, and there is no error.
  #      "@type": "type.googleapis.com/chronicle.backstory.v1.RunRuleResponse"
  #   }
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return Operation(response.json())


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
      "-oi",
      "--operation_id",
      type=str,
      required=True,
      help="detection operation ID ('rulejob_jo_<UUID>')")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  operation_details = get_operation(session, args.operation_id)
  print(operation_details)
