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
"""Executable sample for creating a Workspace Alerts Feed.

Creating other feeds requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_workspace_alerts_feed(http_session: requests.AuthorizedSession,
                                 tokenendpoint: str, issuer: str, subject: str,
                                 audience: str, privatekey: str,
                                 workspacecustomerid: str, displayname: str
                                 ) -> Mapping[str, Any]:
  """Creates a new Workspace Alerts feed.

  Args:
    http_session: Authorized session for HTTP requests.
    tokenendpoint: A string which represents endpoint to connect to.
    issuer: A string which represents issuer of the claims.
    subject: A string which represents subject of the claims.
    audience: A string which represents audience of the claims.
    privatekey: A string which represents private key of the credential. Please
      note private key should have new line characters in it, sample at:
        http://phpseclib.sourceforge.net/rsa/examples.html
    workspacecustomerid: A string which represents workspace customer id.
    displayname: A string which represents customer-provided feed name.

  Returns:
    New Workspace Alerts Feed.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/feeds/"
  body = {
      "details": {
          "feedSourceType": "API",
          "logType": "WORKSPACE_ALERTS",
          "workspaceAlertsSettings": {
              "authentication": {
                  "tokenEndpoint": tokenendpoint,
                  "claims": {
                      "issuer": issuer,
                      "subject": subject,
                      "audience": audience
                  },
                  "rsCredentials": {
                      "private_key": privatekey
                  }
              },
              "workspaceCustomerId": workspacecustomerid.lstrip("C"),
          }
      },
      "display_name": displayname,
  }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "name": "feeds/cf91de35-1256-48f5-8a36-9503e532b879",
  #   "display_name": "my feed name",
  #   "details": {
  #     "logType": "WORKSPACE_ACTIVITY",
  #     "feedSourceType": "API",
  #     "workspaceAlertsSettings": {
  #       "authentication": {
  #         "tokenEndpoint": "endpoint.example.com",
  #         "claims": {
  #           "issuer": "issuer_example",
  #           "subject": "subject_example",
  #           "audience": "audience_example"
  #         },
  #         "rsCredentials": {
  #           "privateKey": "REDACTED"
  #         }
  #       },
  #       "workspaceCustomerId": "9999",
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
      "--claimsissuer",
      type=str,
      required=True,
      help="claims issuer")
  parser.add_argument(
      "-cs",
      "--claimssubject",
      type=str,
      required=True,
      help="claims subject")
  parser.add_argument(
      "-ca",
      "--claimsaudience",
      type=str,
      required=True,
      help="claims audience")
  parser.add_argument(
      "-cp",
      "--credentialsprivatekey",
      type=str,
      required=True,
      help="credentials private key")
  parser.add_argument(
      "-wci",
      "--workspacecustomerid",
      type=str,
      required=True,
      help="workspace customer id")
  parser.add_argument(
      "-dn",
      "--displayname",
      type=str,
      required=False,
      help="display name")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_feed = create_workspace_alerts_feed(session, args.tokenendpoint,
                                          args.claimsissuer, args.claimssubject,
                                          args.claimsaudience,
                                          args.credentialsprivatekey,
                                          args.workspacecustomerid,
                                          args.displayname)
  print(json.dumps(new_feed, indent=2))
