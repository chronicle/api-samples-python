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
"""Executable and reusable sample for deleting a detection operation."""

import argparse
import re

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

OPERATION_ID_PATTERN = re.compile(
    r"rulejob_jo_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
    r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def delete_operation(http_session: requests.AuthorizedSession,
                     operation_id: str):
  """Deletes a specific asynchronous detection operation.

  This indicates that the client is no longer interested in the operation's
  result. Deletion includes an implicit and internal call to cancel_operation(),
  but unlike cancellation you can no longer query the details and latest state
  of an operation after calling delete_operation().

  Args:
    http_session: Authorized session for HTTP requests.
    operation_id: Unique ID of the asynchronous detection operation to delete
      ("rulejob_jo_<UUID>").

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not OPERATION_ID_PATTERN.fullmatch(operation_id):
    raise ValueError(f"Invalid detection operation ID: '{operation_id}' != " +
                     "'rulejob_jo_<UUID>'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/operations/{operation_id}"
  response = http_session.request("DELETE", url)
  # Expected server response:
  # {}

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()


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
  delete_operation(session, args.operation_id)
