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
"""Executable sample for creating a Okta feed.

Creating other feeds requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_okta_feed(http_session: requests.AuthorizedSession,
                     secret: str, hostname: str, displayname: str
                     ) -> Mapping[str, Any]:
  """Creates a new Okta feed.

  Args:
    http_session: Authorized session for HTTP requests.
    secret: A string which represents Okta auth user's secret.
    hostname: A string which represents hostname to connect to.
    displayname: A string which describes the feed.

  Returns:
    New Okta Feed.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/feeds/"
  body = {
      "details": {
          "feedSourceType": "API",
          "logType": "OKTA",
          "oktaSettings": {
              "authentication": {
                  "headerKeyValues": [{
                      "key": "Authorization",
                      "value": secret
                  }]
              },
              "hostname": hostname
          }
      },
      "display_name": displayname,
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "name": "feeds/7921585c-b0b5-490a-a8bd-ff011d7011a5",
  #   "display_name": "my feed name",
  #   "details": {
  #     "logType": "OKTA",
  #     "feedSourceType": "API",
  #     "oktaSettings": {
  #       "authentication": {
  #         "headerKeyValues": [
  #           {
  #             "key": "Authorization",
  #             "value": "secret_example"
  #           }
  #         ]
  #       },
  #       "hostname": "hostname_example"
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
      "-s",
      "--secret",
      type=str,
      required=True,
      help="secret")
  parser.add_argument(
      "-hn",
      "--hostname",
      type=str,
      required=True,
      help="hostname")
  parser.add_argument(
      "-dn",
      "--displayname",
      type=str,
      required=False,
      help="display name")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_feed = create_okta_feed(session, args.secret, args.hostname,
                              args.displayname)
  print(json.dumps(new_feed, indent=2))
