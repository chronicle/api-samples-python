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
"""Executable and reusable sample for cancelling a detection operation."""

import argparse
import re

from . import chronicle_auth
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"

OPERATION_ID_PATTERN = re.compile(
    r"rulejob_jo_[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-" +
    r"[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}")


def cancel_operation(http_session: requests.AuthorizedSession,
                     operation_id: str):
  """Starts asynchronous cancellation of a specific detection operation.

  This cancels operations in progress which were started by run_rule(), as well
  as live-rule operations which were started by enable_live_rule(). There is no
  effect to calling this on an operation which is already done.

  Either way, the server makes a best effort to cancel this operation, but
  success is not guaranteed.

  Note that even on successful cancellation, the operation is not deleted, you
  can still check its details with get_operation() until you explicitly call
  delete_operation().

  Args:
    http_session: Authorized session for HTTP requests.
    operation_id: Unique ID of the asynchronous detection operation to cancel
      ("rulejob_jo_<UUID>").

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if not OPERATION_ID_PATTERN.fullmatch(operation_id):
    raise ValueError(f"Invalid detection operation ID: '{operation_id}' != " +
                     "'rulejob_jo_<UUID>'.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/operations/{operation_id}:cancel"
  response = http_session.request("POST", url)
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
  cancel_operation(session, args.operation_id)
