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
# TODO(b/193595445): Add documentation link for enetity format once it's done.
r"""Executable and reusable sample for ingesting entities.

WARNING: This script makes use of the Ingestion API V2. V2 is currently only in
preview for certain Chronicle customers. Please reach out to your Chronicle
representative if you wish to use this API.

An entity describes some Noun that is known to the customer. It is used to
package information about Nouns that is discovered separately from event
ingestion. Examples of real-world entities are users, employees, devices, etc.
This sample ingests entities in a structured format, instead of as raw logs.

It accepts a path to a file (--json_entities_file) that contains an array of
JSON formatted Entity data. See ./example_input/sample_entities.json for an
example.

So, assuming you're created a credentials file at ~/.chronicle_credentials.json,
you can run this command using the sample input like so:

$ create_entities --customer_id=<your customer UUID> \
  --log_type=<log type> \
  --json_entities_file=./example_input/sample_entities.json

If you're not sure of what log type you should be using, you can get a set of
valid log types by running list_log_types.py and find an appropriate one.
"""

import argparse
import json

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

INGESTION_API_BASE_URL = "https://malachiteingestion-pa.googleapis.com"
AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]


def create_entities(http_session: requests.AuthorizedSession, customer_id: str,
                    log_type: str, json_entities: str) -> None:
  """Sends a collection of Entity data to the Chronicle backend for ingestion.

  An Entity is a structured representation of a real-world object like user,
  device etc. regardless of the log source.

  Args:
    http_session: Authorized session for HTTP requests.
    customer_id: A string containing the UUID for the Chronicle customer.
    log_type: A string containing the log type.
    json_entities: A collection of Entity protos in (serialized) JSON format.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{INGESTION_API_BASE_URL}/v2/entities:batchCreate"
  body = {
      "customer_id": customer_id,
      "log_type": log_type,
      "entities": json.loads(json_entities),
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
      "--log_type", type=str, required=True, help="the log type")
  parser.add_argument(
      "--json_entities_file",
      type=argparse.FileType("r"),
      required=True,
      help="path to a file (or \"-\" for STDIN) containing a list of Entity "
      "events in JSON format")

  args = parser.parse_args()
  INGESTION_API_BASE_URL = regions.url(INGESTION_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(
      args.credentials_file, scopes=AUTHORIZATION_SCOPES)
  create_entities(session, args.customer_id, args.log_type,
                  args.json_entities_file.read())
