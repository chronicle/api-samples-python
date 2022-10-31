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
"""Executable sample for creating a syslog collector.

Creating other collectors requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

# CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"
CHRONICLE_API_BASE_URL = "https://test-backstory.sandbox.googleapis.com"


def create_collector(http_session: requests.AuthorizedSession, forwarderName: str) -> Mapping[str, Any]:
  """Creates a collector on an existing forwarder.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    Collector

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/{forwarderName}/collectors"
  body = {
    "display_name": "FileCollector",
    "config": {
      "log_type": "WINDOWS_DNS",
      "file_settings": {
        "file_path": "/path/to/log.file"
      }
    }
  }

  # body = {
  #   "display_name": "SyslogCollector1",
  #   "config": {
  #     "log_type": "PAN_FIREWALL",
  #     "syslog_settings": {
  #       "protocol": "TCP",
  #       "address": "0.0.0.0",
  #       "port": 10514,
  #     }
  #   }
  # }

  # body = {
  #   "display_name": "SplunkCollector",
  #   "config": {
  #     "log_type": "WINDOWS_DNS",
  #     "splunk_settings": {
  #       "host": "127.0.0.1",
  #       "port": 8089,
  #       "query_string": "search index=* sourcetype=dns",
  #       "query_mode": "realtime",
  #       "authentication": {
  #         "username": "admin",
  #         "password": "pass",
  #       }
  #     }
  #   }
  # }

  response = http_session.request("POST", url, json=body)
  # Example server response for Syslog collector:
  # {
  #   "name": "forwarders/50df8cb4-03de-4ccb-b10d-7a05b2dace10/collectors/a5b298f0-549c-4747-8da3-1d4edb161313",
  #   "displayName": "TestCollector1",
  #   "config": {
  #     "logType": "PAN_FIREWALL",
  #     "maxSecondsPerBatch": 10,
  #     "maxBytesPerBatch": "1048576",
  #     "syslogSettings": {
  #       "protocol": "TCP",
  #       "address": "0.0.0.0",
  #       "port": 10514,
  #       "bufferSize": "65536",
  #       "connectionTimeout": 60
  #     }
  #   },
  #   "state": "ACTIVE"
  # }

  # Example server response for Splunk collector:
  # {
  #   "name": "forwarders/86372ddf-3736-42e8-a78e-aee1a6e3517b/collectors/52d658fc-2d51-4a8a-8986-425195a28ffb",
  #   "displayName": "SplunkCollector",
  #   "config": {
  #     "logType": "WINDOWS_DNS",
  #     "maxSecondsPerBatch": 10,
  #     "maxBytesPerBatch": "1048576",
  #     "splunkSettings": {
  #       "host": "127.0.0.1",
  #       "minimumWindowSize": 10,
  #       "maximumWindowSize": 30,
  #       "queryString": "search index=* sourcetype=dns",
  #       "queryMode": "realtime",
  #       "port": 8089
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
    "-f",
    "--forwarder",
    type=str,
    required=True,
    help="name of the forwarder on which to add the collector")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_forwarder = create_collector(session, args.forwarder)
  print(json.dumps(new_forwarder, indent=2))
