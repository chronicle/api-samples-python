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
r"""Executable and reusable sample for ingesting unstructured log entries.

WARNING: This script makes use of the Ingestion API V2. V2 is currently only in
preview for certain Chronicle customers. Please reach out to your Chronicle
representative if you wish to use this API.

This command accepts a path to a file (--logs_file) containing raw logs, one per
line. The format of the log depends on the log type (specified by the --log_type
flag). See ./example_input/sample_unstructured_log_entries.txt for an example
log for the BIND_DNS log type.

So, assuming you're created a credentials file at ~/.chronicle_credentials.json,
you can run this command using the sample imput like so:

$ create_unstructured_log_entries --customer_id=<your customer UUID> \
  --log_type=BIND_DNS \
  --logs_file=./example_input/sample_unstructured_log_entries.txt

API reference:
https://cloud.google.com/chronicle/docs/reference/ingestion-api#unstructuredlogentries
"""

import argparse

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

INGESTION_API_BASE_URL = "https://malachiteingestion-pa.googleapis.com"
AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]


def create_logs(http_session: requests.AuthorizedSession, log_type: str,
                customer_id: str, logs_text: str) -> None:
  """Sends unstructured log entries to the Chronicle backend for ingestion.

  Args:
    http_session: Authorized session for HTTP requests.
    log_type: Log type for a feed. To see supported log types run
      list_supported_log_types.py
    customer_id: A string containing the UUID for the Chronicle customer.
    logs_text: A string containing logs delimited by new line characters. The
      total size of this string may not exceed 1MB or the resultsing request to
      the ingestion API will fail.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{INGESTION_API_BASE_URL}/v2/unstructuredlogentries:batchCreate"
  entries = [{"logText": t} for t in logs_text.splitlines()]
  body = {
      "customerId": customer_id,
      "logType": log_type,
      "entries": entries,
  }

  response = http_session.request("POST", url, json=body)
  response.raise_for_status()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "--log_type",
      type=str,
      required=True,
      help="log type")
  parser.add_argument(
      "--customer_id",
      type=str,
      required=True,
      help="the customer UUID")
  parser.add_argument(
      "--logs_file",
      type=argparse.FileType("r"),
      required=True,
      help="path to a file (or \"-\" for STDIN) containing logs, one log per "
      "line, whose format varies by log type, and whose total size must not "
      "exceed 1MB events")

  args = parser.parse_args()
  INGESTION_API_BASE_URL = regions.url(INGESTION_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file,
                                                   scopes=AUTHORIZATION_SCOPES)
  create_logs(session, args.log_type, args.customer_id, args.logs_file.read())
