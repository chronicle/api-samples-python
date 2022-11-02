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
"""Executable sample for creating a Chronicle forwarder.

Creating other forwarders requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_forwarder(
    http_session: requests.AuthorizedSession) -> Mapping[str, Any]:
  """Creates a new Chronicle forwarder.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    Newly created Chronicle Forwarder.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/forwarders/"

  # The minimal configuration requires only a name.
  body = {
      "display_name": "TestForwarder",
  }

  # Example of a more advanced Forwarder configuration.
  # body = {
  #   "display_name": "TestForwarder2",
  #   "config": {
  #     "upload_compression": True,
  #     "metadata": {
  #       "asset_namespace": "FORWARDER",
  #       "labels": [
  #         {
  #           "key": "office",
  #           "value": "corporate",
  #         },
  #         {
  #           "key": "building",
  #           "value": "001"
  #         }
  #       ]
  #     },
  #     "regex_filters": [
  #       {
  #         "description": "TestFilter",
  #         "regexp": ".*",  # Must be valid RE2 syntax
  #         "behavior": "ALLOW",  # Allowed values: ALLOW, BLOCK
  #       },
  #     ],
  #     "server_settings": {
  #       "state": "ACTIVE",  # Allowed values: ACTIVE, SUSPENDED
  #     }
  #   }
  # }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "name": "forwarders/{forwarderUUID}",
  #   "displayName": "TestForwarder",
  #   "config": {
  #     "uploadCompression": true
  #   },
  #   "state": "ACTIVE"
  # }

  # # Expected server response for advanced configuration:
  # {
  #   "name": "forwarders/{forwarderUUID}",
  #   "displayName": "TestForwarder2",
  #   "config": {
  #     "uploadCompression": true,
  #     "metadata": {
  #       "assetNamespace": "FORWARDER",
  #       "labels": [
  #         {
  #           "key": "office",
  #           "value": "corporate"
  #         },
  #         {
  #           "key": "building",
  #           "value": "001"
  #         }
  #       ]
  #     },
  #     "regexFilters": [
  #       {
  #         "description": "TestFilter",
  #         "regexp": ".*",
  #         "behavior": "ALLOW"
  #       }
  #     ],
  #     "serverSettings": {
  #       "gracefulTimeout": 15,
  #       "drainTimeout": 10,
  #       "httpSettings": {
  #         "port": 8080,
  #         "host": "0.0.0.0",
  #         "readTimeout": 3,
  #         "readHeaderTimeout": 3,
  #         "writeTimeout": 3,
  #         "idleTimeout": 3,
  #         "routeSettings": {
  #           "availableStatusCode": 204,
  #           "readyStatusCode": 204,
  #           "unreadyStatusCode": 503
  #         }
  #       },
  #       "state": "ACTIVE"
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

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_forwarder = create_forwarder(session)
  print(json.dumps(new_forwarder, indent=2))
