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
"""Executable and reusable sample for listing supported log types.

WARNING: This script makes use of the Ingestion API V2. V2 is currently only in
preview for certain Chronicle customers. Please reach out to your Chronicle
representative if you wish to use this API.

API reference:
https://cloud.google.com/chronicle/docs/reference/ingestion-api#logtypes
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

INGESTION_API_BASE_URL = "https://malachiteingestion-pa.googleapis.com"
AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/malachite-ingestion"]


def list_log_types(
    http_session: requests.AuthorizedSession) -> Mapping[str, Any]:
  """Retrieves a list of log types suitable for Chronicle ingestion.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    The log types suitable for Chronicle ingestion.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{INGESTION_API_BASE_URL}/v2/logtypes"

  response = http_session.request("GET", url)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)

  args = parser.parse_args()
  INGESTION_API_BASE_URL = regions.url(INGESTION_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file,
                                                   scopes=AUTHORIZATION_SCOPES)
  print(json.dumps(list_log_types(session), indent=2))
