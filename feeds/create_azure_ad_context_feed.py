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
"""Executable sample for creating a Azure AD Context Feed.

Creating other feeds requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_azure_ad_context_feed(http_session: requests.AuthorizedSession,
                                 tokenendpoint: str, clientid: str,
                                 clientsecret: str, retrievedevices: bool,
                                 retrievegroups: bool) -> Mapping[str, Any]:
  """Creates a new Azure AD Context feed.

  Args:
    http_session: Authorized session for HTTP requests.
    tokenendpoint: A string which represents endpoint to connect to.
    clientid: A string which represents Id of the credential to use.
    clientsecret: A string which represents secret of the credential to use.
    retrievedevices: A boolean to indicate whether to retrieve devices or not.
    retrievegroups: A boolean to indicate whether to retrieve groups or not.

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
          "logType": "AZURE_AD_CONTEXT",
          "azureAdContextSettings": {
              "authentication": {
                  "tokenEndpoint": tokenendpoint,
                  "clientId": clientid,
                  "clientSecret": clientsecret
              },
              "retrieveDevices": retrievedevices,
              "retrieveGroups": retrievegroups
          }
      }
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "name": "feeds/e0eb5fb0-8fbd-4f0f-b063-710943ad7812",
  #   "details": {
  #     "logType": "AZURE_AD_CONTEXT",
  #     "feedSourceType": "API",
  #     "azureAdContextSettings": {
  #       "authentication": {
  #         "tokenEndpoint": "tokenendpoint.example.com",
  #         "clientId": "clientid_example",
  #         "clientSecret": "clientsecret_example"
  #       },
  #       "retrieveDevices": true
  #     }
  #   },
  #   "feedState": "PENDING_ENABLEMENT"
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
      "-te",
      "--tokenendpoint",
      type=str,
      required=True,
      help="token endpoint")
  parser.add_argument(
      "-ci",
      "--clientid",
      type=str,
      required=True,
      help="client id")
  parser.add_argument(
      "-cs",
      "--clientsecret",
      type=str,
      required=True,
      help="client secret")
  parser.add_argument(
      "-rd",
      "--retrievedevices",
      type=bool,
      required=True,
      help="retrieve devices")
  parser.add_argument(
      "-rg",
      "--retrievegroups",
      type=str,
      required=True,
      help="retrieve groups")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_feed = create_azure_ad_context_feed(session, args.tokenendpoint,
                                          args.clientid, args.clientsecret,
                                          args.retrievedevices,
                                          args.retrievegroups)
  print(json.dumps(new_feed, indent=2))
