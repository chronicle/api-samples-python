#!/usr/bin/env python3

# Copyright 2021 Google LLC
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
"""Executable sample for creating a Cortex XDR feed.

For more documentation on this specific type of feed, see:
https://docs.paloaltonetworks.com/content/dam/techdocs/en_US/pdf/cortex/cortex-xdr/cortex-xdr-api/cortex-xdr-api.pdf

Creating other feeds requires changing this sample code.
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def create_cortex_xdr_feed(http_session: requests.AuthorizedSession,
                           name: str,
                           hostname: str) -> Mapping[str, Any]:
  """Creates a new Cortex XDR feed.

  Args:
    http_session: Authorized session for HTTP requests.
    name: Unique name for the feed.
    hostname: A string in the form "api-{fqdn}", provided to the customer by
      Cortex XDR, e.g. "api-host.xdr.domain.paloaltonetworks.com".

  Returns:
    New Cortex XDR Feed.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/feeds/"
  body = {
      "name": name,
      "feedDetails": {
          "feedType": "CORTEX_XDR",
          "cortexXdrSettings": {
              "hostname": hostname,
          },
      },
      "feedState": "PENDING_ENABLEMENT",
    }

  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   "feedDetails": {
  #     "cortexXdrSettings": {
  #       "hostname": "<hostname>",
  #     },
  #     "feedType": "CORTEX_XDR",
  #   },
  #   "name": "<name>",
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
      help="unique name for the feed")
  parser.add_argument(
      "-ho",
      "--hostname",
      type=str,
      required=True,
      help="unique hostname")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  new_feed = create_cortex_xdr_feed(session, args.name, args.hostname)
  print(json.dumps(new_feed, indent=2))
