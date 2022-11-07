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
"""Executable and reusable sample for retrieving a list of collectors."""

import argparse
import json
from typing import Mapping, Any

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def list_collectors(http_session: requests.AuthorizedSession,
                    name: str) -> Mapping[str, Any]:
  """Retrieves all collectors for the tenant.

  Args:
    http_session: Authorized session for HTTP requests.
    name: Resource name for the Forwarder (forwarders/{UUID}).

  Returns:
    Array containing each collector belonging to the forwarder.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/{name}/collectors"

  response = http_session.request("GET", url)
  # Example server response:
  # {
  #   "collectors": [
  #     {
  #       "name": "forwarders/{forwarderUUID}/collectors/{collectorUUID}",
  #       "displayName": "SplunkCollector",
  #       "config": {
  #         "logType": "WINDOWS_DNS",
  #         "maxSecondsPerBatch": 10,
  #         "maxBytesPerBatch": "1048576",
  #         "splunkSettings": {
  #           "host": "127.0.0.1",
  #           "minimumWindowSize": 10,
  #           "maximumWindowSize": 30,
  #           "queryString": "search index=* sourcetype=dns",
  #           "queryMode": "realtime",
  #           "port": 8089
  #         }
  #       },
  #       "state": "ACTIVE"
  #     },
  #     {
  #       "name": "forwarders/{forwarderUUID}/collectors/{collectorUUID}",
  #       "displayName": "SyslogCollector1",
  #       "config": {
  #         "logType": "PAN_FIREWALL",
  #         "maxSecondsPerBatch": 10,
  #         "maxBytesPerBatch": "1048576",
  #         "syslogSettings": {
  #           "protocol": "TCP",
  #           "address": "0.0.0.0",
  #           "port": 10514,
  #           "bufferSize": "65536",
  #           "connectionTimeout": 60
  #         }
  #       },
  #       "state": "ACTIVE"
  #     }
  #   ]
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
      "-f",
      "--forwarder_name",
      type=str,
      required=True,
      help="resource name for the Forwarder (forwarders/{UUID})")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  print(json.dumps(list_collectors(session, args.forwarder_name), indent=2))
