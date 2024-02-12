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
r"""Executable and reusable sample for getting a Reference List.

Usage:
  python -m lists.v1alpha.get_list \
    --project_id=<PROJECT_ID>   \
    --project_instance=<PROJECT_INSTANCE> \
    --name="COLDRIVER_SHA256"

API reference:
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists/get
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#ReferenceList
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#ReferenceListEntry
"""

import argparse
import json
from typing import Dict

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def get_list(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    name: str,
) -> Dict[str, any]:
  """Gets a Reference List.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    name: name that identifies the list to get.

  Returns:
    Dictionary representation of the Reference List

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      proj_region
  )
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/referenceLists/{name}"

  response = http_session.request("GET", url)
  # Expected server response is described in:
  # https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#ReferenceList
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-n", "--name", type=str, required=True,
      help="name that identifies the list to get"
  )
  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  a_list = get_list(
      auth_session,
      args.project_id,
      args.project_instance,
      args.region,
      args.name,
  )
  print(json.dumps(a_list, indent=2))
