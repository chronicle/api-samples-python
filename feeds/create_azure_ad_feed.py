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
"""Executable sample for creating a Azure AD Feed.

Creating other feeds requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_azure_ad_feed(http_session: requests.AuthorizedSession,
                         tenantid: str, clientid: str,
                         clientsecret: str, displayname: str
                         ) -> Mapping[str, Any]:
  """Creates a new Azure AD feed.

  Args:
    http_session: Authorized session for HTTP requests.
    tenantid: A string which represents the tenant id.
    clientid: A string which represents Id of the credential to use.
    clientsecret: A string which represents secret of the credential to use.
    displayname: A string which describes the feed.

  Returns:
    New Azure AD Feed.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/feeds/"
  body = {
      "details": {
          "feedSourceType": "API",
          "logType": "AZURE_AD",
          "azureAdSettings": {
              "authentication": {
                  "clientId": clientid,
                  "clientSecret": clientsecret
              },
              "tenantId": tenantid,
          }
      },
      "display_name": displayname,
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  #   {
  #   "name": "feeds/cf49ebc5-e7bf-4562-8061-cab43cecba35",
  #   "display_name": "my feed name",
  #   "details": {
  #     "logType": "AZURE_AD",
  #     "feedSourceType": "API",
  #     "azureAdSettings": {
  #       "authentication": {
  #         "clientId": "clientid_example",
  #         "clientSecret": "clientsecret_example"
  #       },
  #       "tenantId": "0fc279f9-fe30-41be-97d3-abe1d7681418"
  #     }
  #   },
  #   "feedState": "ACTIVE"
  #  }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-ti", "--tenantid", type=str, required=True, help="tenant id")
  parser.add_argument(
      "-ci", "--clientid", type=str, required=True, help="client id")
  parser.add_argument(
      "-cs", "--clientsecret", type=str, required=True, help="client secret")
  parser.add_argument(
      "-dn", "--displayname", type=str, required=False,
      help="display name")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_feed = create_azure_ad_feed(session, args.tenantid, args.clientid,
                                  args.clientsecret, args.displayname)
  print(json.dumps(new_feed, indent=2))
