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
"""Executable sample for creating a collector.

Creating other collectors requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_collector(http_session: requests.AuthorizedSession,
                     forwarder_name: str) -> Mapping[str, Any]:
  """Creates a collector on an existing forwarder.

  Args:
    http_session: Authorized session for HTTP requests.
    forwarder_name: Resource name for the Forwarder (forwarders/{UUID}).

  Returns:
    Collector

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/{forwarder_name}/collectors"

  body = {
      "display_name": "SyslogCollector",
      "config": {
          "log_type": "PAN_FIREWALL",
          "syslog_settings": {
              "protocol": "TCP",
              "address": "0.0.0.0",
              "port": 10514,
          }
      }
  }

  # # Example of a File collector:
  # body = {
  #     "display_name": "FileCollector",
  #     "config": {
  #         "log_type": "WINDOWS_DNS",
  #         "file_settings": {
  #             "file_path": "/path/to/log.file"
  #         }
  #     }
  # }

# # Example of a Splunk collector:
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
  #   "name": "forwarders/{forwarderUUID}/collectors/{collectorUUID}",
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
  #   "name": "forwarders/{forwarderUUID}/collectors/{collectorUUID}",
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
      "--forwarder_name",
      type=str,
      required=True,
      help="resource name for the Forwarder (forwarders/{UUID})")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_forwarder = create_collector(session, args.forwarder_name)
  print(json.dumps(new_forwarder, indent=2))
