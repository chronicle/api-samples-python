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
"""Executable and reusable sample for retrieving a list of feeds."""

import argparse
import json
from typing import Mapping, Any

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_feeds(http_session: requests.AuthorizedSession) -> Mapping[str, Any]:
  """Retrieves all feeds for the tenant.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    Array containing each line of the feed's content.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/feeds"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  # "feeds": [
  #   {
  #     "name": "feeds/19e82867-ab6d-4955-b9c8-bd4aee189439",
  #     "details": {
  #       "logType": "AZURE_AD_CONTEXT",
  #       "feedSourceType": "API",
  #       "azureAdContextSettings": {}
  #     },
  #     "feedState": "INACTIVE"
  #   },
  #   {
  #     "name": "feeds/cdc096a5-93a8-4854-94d9-c05cf0c14d47",
  #     "details": {
  #       "logType": "PAN_PRISMA_CLOUD",
  #       "feedSourceType": "API",
  #       "panPrismaCloudSettings": {
  #         "hostname": "api2.prismacloud.io"
  #       }
  #     },
  #     "feedState": "ACTIVE"
  #   }
  # ]
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
  print(json.dumps(list_feeds(session), indent=2))
