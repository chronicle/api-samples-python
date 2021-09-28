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
r"""Executable and reusable sample for ingesting events in UDM format.

WARNING: This script makes use of the Ingestion API V2. V2 is currently only in
preview for certain Chronicle customers. Please reach out to your Chronicle
representative if you wish to use this API.

The Unified Data Model (UDM) is a way of representing events across all log
sources. See
https://cloud.google.com/chronicle/docs/unified-data-model/udm-field-list for a
description of UDM fields, and see
https://cloud.google.com/chronicle/docs/unified-data-model/format-events-as-udm
for how to describe a log as an event in UDM format.

This command accepts a path to a file (--json_events_file) that contains an
array of JSON formatted events in UDM format. See
./example_input/sample_udm_events.json for an example.

So, assuming you've created a credentials file at ~/.chronicle_credentials.json,
you can run this command using the sample imput like so:

$ create_udm_events --customer_id=<your customer UUID> \
  --json_events_file=./example_input/sample_udm_events.json

API reference:
https://cloud.google.com/chronicle/docs/reference/ingestion-api#udmevents
https://cloud.google.com/chronicle/docs/reference/udm-field-list
https://cloud.google.com/chronicle/docs/unified-data-model/udm-usage
"""

import argparse
import json

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

INGESTION_API_BASE_URL = "https://malachiteingestion-pa.googleapis.com"
AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]


def create_udm_events(http_session: requests.AuthorizedSession,
                      customer_id: str, json_events: str) -> None:
  """Sends a collection of UDM events to the Chronicle backend for ingestion.

  A Unified Data Model (UDM) event is a structured representation of an event
  regardless of the log source.

  Args:
    http_session: Authorized session for HTTP requests.
    customer_id: A string containing the UUID for the Chronicle customer.
    json_events: A collection of UDM events in (serialized) JSON format.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{INGESTION_API_BASE_URL}/v2/udmevents:batchCreate"
  body = {
      "customerId": customer_id,
      "events": json.loads(json_events),
  }

  response = http_session.request("POST", url, json=body)
  response.raise_for_status()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "--customer_id", type=str, required=True, help="the customer UUID")
  parser.add_argument(
      "--json_events_file",
      type=argparse.FileType("r"),
      required=True,
      help="path to a file (or \"-\" for STDIN) containing a list of UDM "
      "events in json format")

  args = parser.parse_args()
  INGESTION_API_BASE_URL = regions.url(INGESTION_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(
      args.credentials_file, scopes=AUTHORIZATION_SCOPES)
  create_udm_events(session, args.customer_id, args.json_events_file.read())
