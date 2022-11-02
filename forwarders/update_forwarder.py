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
"""Executable and reusable sample for updating a forwarder."""

import argparse
import json
from typing import Mapping, Any

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def update_forwarder(http_session: requests.AuthorizedSession,
                     name: str) -> Mapping[str, Any]:
  """Updates a forwarder.

  Args:
    http_session: Authorized session for HTTP requests.
    name: Resource name for the Forwarder (forwarders/{UUID}).

  Returns:
    The entire forwarder configuration with update(s) appled.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/{name}"

  body = {
      "display_name": "UpdatedForwarder",
      "config": {
          "metadata": {
              "labels": [{
                  "key": "office",
                  "value": "corporate",
              }]
          }
      }
  }

  update_fields = ["display_name", "config.metadata.labels"]
  params = {"update_mask": ",".join(update_fields)}

  response = http_session.request("PATCH", url, params=params, json=body)
  # Expected server response:
  # {
  #   "name": "forwarders/{forwarderUUID}",
  #   "displayName": "UpdatedForwarder",
  #   "config": {
  #     "uploadCompression": true,
  #     "metadata": {
  #       "labels": [
  #         {
  #           "key": "office",
  #           "value": "corporate"
  #         }
  #       ]
  #     }
  #   },
  #   "state": "ACTIVE"
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
      "-n",
      "--name",
      type=str,
      required=True,
      help="resource name for the Forwarder (forwarders/{UUID})")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  print(json.dumps(update_forwarder(session, args.name), indent=2))
