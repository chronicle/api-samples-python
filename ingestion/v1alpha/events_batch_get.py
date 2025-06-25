#!/usr/bin/env python3

# Copyright 2025 Google LLC
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
# pylint: disable=line-too-long
r"""Executable and reusable v1alpha API sample for batch getting events from Chronicle.

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/batchGet
"""
# pylint: enable=line-too-long

import argparse
import base64
import json

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def batch_get_events(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    event_ids: str
) -> None:
  """Batch get events from Chronicle using the Events BatchGet API.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid w/ dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    event_ids: JSON string containing a list of event IDs to retrieve.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
        (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.events.batchGet
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/events:batchGet"
  # pylint: enable=line-too-long

  # Convert event IDs to URL-encoded Base64 and create query parameters
  event_ids_list = json.loads(event_ids)
  encoded_ids = [
      base64.urlsafe_b64encode(id.encode()).decode() for id in event_ids_list
  ]
  query_params = "&".join([f"names={id}" for id in encoded_ids])

  url = f"{url}?{query_params}"

  response = http_session.request("GET", url)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()

  print(json.dumps(response.json(), indent=2))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument("--event_ids",
                      type=str,
                      required=True,
                      help='JSON string containing a list of event IDs to '
                      'retrieve (e.g., \'["id1", "id2"]\')')

  args = parser.parse_args()
  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  batch_get_events(auth_session, args.project_id, args.project_instance,
                   args.region, args.event_ids)
