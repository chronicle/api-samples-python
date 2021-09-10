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
"""Executable and reusable sample for retrieving an error.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#geterror
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def get_error(http_session: requests.AuthorizedSession,
              error_id: str) -> Mapping[str, Any]:
  """Get error.

  Args:
    http_session: Authorized session for HTTP requests.
    error_id: Id of the error to get information for.

  Returns:
    Detection information.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/health/errors/{error_id}"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #    "category": "RULES_EXECUTION_ERROR",
  #    "errorId": "ed_<UUID>",
  #    "errorTime": "yyyy-mm-ddThh:mm:ssZ",
  #    "ruleExecution": {
  #       "ruleId": "ru_<UUID>",
  #       "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #       "windowEndTime": "yyyy-mm-ddThh:mm:ssZ",
  #       "windowStartTime": "yyyy-mm-ddThh:mm:ssZ"
  #    },
  #    "text": "<error message>"
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-ei",
      "--error_id",
      type=str,
      required=True,
      help="error ID (for Detect errors: 'ed_<UUID>')")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  error = get_error(session, args.error_id)
  print(json.dumps(error, indent=2))
