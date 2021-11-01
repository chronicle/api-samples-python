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
"""Executable and reusable sample for deleting a GCP association.

In Chronicle, customers can associate their GCP organizations with their
Chronicle instances. This example provides a programmatic way to delete such
association.
"""

import argparse
import sys
from typing import Optional, Sequence

from google.auth.transport import requests

from common import chronicle_auth

SERVICE_MANAGEMENT_API_BASE_URL = "https://chronicleservicemanager.googleapis.com"

AUTHORIZATION_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  parser.add_argument(
      "--organization_id",
      type=int,
      required=True,
      help="the GCP organization ID for the association")

  # Sanity checks for the command-line arguments.
  parsed_args = parser.parse_args(args)
  if parsed_args.organization_id >= 2**64 or parsed_args.organization_id < 0:
    print("Error: organization ID should not be bigger than 2^64")
    return None

  return parsed_args


def delete_gcp_association(http_session: requests.AuthorizedSession,
                           organization_id: int) -> None:
  """Deletes a GCP association with Chronicle.

  Args:
    http_session: Authorized session for HTTP requests.
    organization_id: GCP organization ID for the association.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  name = f"organizations/{organization_id}/gcpAssociations/{organization_id}"
  url = f"{SERVICE_MANAGEMENT_API_BASE_URL}/v1/{name}"

  response = http_session.request("DELETE", url)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  session = chronicle_auth.initialize_http_session(
      cli.credentials_file, scopes=AUTHORIZATION_SCOPES)
  delete_gcp_association(session, cli.organization_id)
