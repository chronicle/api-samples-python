#!/usr/bin/env python3

# Copyright 2022 Google LLC
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
"""Executable and reusable sample for retrieving a list of forwarders."""

import argparse
import json
from typing import Mapping, Any

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

# CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"
CHRONICLE_API_BASE_URL = "https://test-backstory.sandbox.googleapis.com"


def list_forwarders(http_session: requests.AuthorizedSession) -> Mapping[str, Any]:
  """Retrieves all forwarders for the tenant.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    Array containing each line of the forwarder's content.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/forwarders"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #     "forwarders": [
  #         {
  #             "name": "forwarders/af2235e5-08d0-45e6-aaf8-98dbfa83a178",
  #             "displayName": "TestForwarder1",
  #             "config": {
  #                 "uploadCompression": true,
  #             },
  #             "state": "ACTIVE"
  #         }
  #     ]
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  print(json.dumps(list_forwarders(session), indent=2))
