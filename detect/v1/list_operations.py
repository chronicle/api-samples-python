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
"""Executable and reusable sample for enumerating all detection operations."""

import argparse
import pprint
from typing import Sequence

from . import chronicle_auth
from . import get_operation
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_operations(http_session: requests.AuthorizedSession,
                    size_limit: int = 0) -> Sequence[get_operation.Operation]:
  """Retrieves details and states of all the operations of your organization.

  This API call does not support pagination at this time.

  Args:
    http_session: Authorized session for HTTP requests.
    size_limit: Maximum number of operations in the response. Must be
      non-negative. Optional - no client-side limit by default.

  Returns:
    All the detection operations of your organization.

  Raises:
    ValueError: Invalid input value.
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  if size_limit < 0:
    raise ValueError(f"Invalid input: size_limit = {size_limit}, must be >= 0.")

  url = f"{CHRONICLE_API_BASE_URL}/v1/operations"
  if size_limit > 0:
    url += f"?page_size={size_limit}"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "operations": [
  #     {
  #       "name": "operations/rulejob_jo_<UUID>",
  #       "metadata": {
  #         "@type": "...",
  #         "ruleId": "ru_<UUID>",
  #         "eventStartTime": "yyyy-mm-ddThh:mm:ssZ",
  #         "eventEndTime": "yyyy-mm-ddThh:mm:ssZ",
  #         "runStartedTime": "yyyy-mm-ddThh:mm:ssZ",
  #         "runCompletedTime": "yyyy-mm-ddThh:mm:ssZ"  <-- IFF "done" is true.
  #       },
  #       "done": true,  <-- If and only if operation's execution is finished.
  #       "error": {"code": <int>, "message": <str>}  <-- IFF there's an error.
  #       "response": {  <-- IFF "done" is true, and there is no error.
  #          "@type": "..."
  #       }
  #     },
  #     ...
  #   ]
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()

  results = []
  for json in response.json()["operations"]:
    results.append(get_operation.Operation(json))
  return results


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "-s",
      "--size_limit",
      type=int,
      default=0,
      help="maximum number of operations to return (default: 0 = no limit)")

  args = parser.parse_args()
  session = chronicle_auth.init_session(
      chronicle_auth.init_credentials(args.credentials_file))
  operations = list_operations(session, args.size_limit)
  pprint.pprint(operations)
