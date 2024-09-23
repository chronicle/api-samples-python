#!/usr/bin/env python3

# Copyright 2024 Google LLC
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
r"""Executable and reusable sample for ingesting STIX Indicators.

 This sample has a dependency not in the requirements.txt file, so you'll need
 to install it first:
 ```
 pip install stix2
 ```
 
 Usage:
 python -m ingestion.create_stix_indicator_iocs \
   --customer_id=<your customer UUID> \
   --stix_file=./example_input/stix2.1.json \
   --credentials_file=<path to ingestion credentials file>
 
 API reference:
 https://cloud.google.com/chronicle/docs/reference/ingestion-api#unstructuredlogentries
"""

import argparse
import datetime
from typing import Optional

from common import chronicle_auth
from common import regions

from google.auth.transport import requests as grequests
import requests
import stix2


INGESTION_API_BASE_URL = "https://malachiteingestion-pa.googleapis.com"
AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]
TLP_LOOKUP = {
    stix2.TLP_WHITE.id: "TLP:WHITE",
    stix2.TLP_GREEN.id: "TLP:GREEN",
    stix2.TLP_AMBER.id: "TLP:AMBER",
    stix2.TLP_RED.id: "TLP:RED",
}
UTC = datetime.timezone.utc


def create_stix_indicator_iocs(
    http_session: grequests.AuthorizedSession,
    customer_id: str,
    stix_text: str,
    log_type: Optional(str) = "STIX",
) -> None:
  """Sends unstructured log entries to the Chronicle backend for ingestion.

  Args:
    http_session: Authorized session for HTTP requests.
    customer_id: A string containing the UUID for the SecOps customer.
    stix_text: stix 2.1 JSON file as a string.
    log_type: Default=STIX. To see supported log types run
      list_supported_log_types.py

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  bundle = stix2.parse(stix_text)

  url = f"{INGESTION_API_BASE_URL}/v2/unstructuredlogentries:batchCreate"
  for entry in bundle.objects:
    if entry.type != "indicator":
      continue  # only Indicators are supported by the current parser

    entries = [{"logText": entry.serialize()}]
    body = {
        "customerId": customer_id,
        "logType": log_type,
        "entries": entries,
        "labels": [
            {
                "key": "ingestion_time",
                "value": datetime.datetime.now(UTC).isoformat(),
            }
        ],
    }
    for marking in entry.get_markings():
      body["labels"].append(
          {"key": "marking", "value": TLP_LOOKUP.get(marking, marking)},
      )
    response = http_session.request("POST", url, json=body)
    try:
      response.raise_for_status()
    except requests.exceptions.HTTPError:
      print(response.json())
    print(response.status_code)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "--log_type", type=str, required=False, default="STIX", help="log type"
  )
  parser.add_argument(
      "--customer_id", type=str, required=True, help="the customer UUID"
  )
  parser.add_argument(
      "--stix_file",
      type=argparse.FileType("r"),
      required=True,
      help='path to a STIX JSON file (or "-" for STDIN)',
  )

  args = parser.parse_args()
  INGESTION_API_BASE_URL = regions.url(INGESTION_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(
      args.credentials_file, scopes=AUTHORIZATION_SCOPES
  )
  create_stix_indicator_iocs(
      session, args.customer_id, args.stix_file.read(), args.log_type,
  )
