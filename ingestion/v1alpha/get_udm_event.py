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
# pylint: disable=line-too-long
r"""Executable and reusable v1alpha API sample for getting a UDM event by ID.

 API reference:
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/get
"""
# pylint: enable=line-too-long

import argparse
import json

from google.auth.transport import requests

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def get_udm_event(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    event_id: str):
  """Get a UDM event by metadata.id.

  A Unified Data Model (UDM) event is a structured representation of an event
  regardless of the log source.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    event_id: URL-encoded Base64 for the UDM Event ID.
  Returns:
    dict/json respresentation of UDM Event
  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.events.get

  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/get
  """
  # pylint: disable=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"https://{proj_region}-chronicle.googleapis.com/v1alpha/{parent}/events/{event_id}"
  # pylint: enable=line-too-long

  response = http_session.request("GET", url)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument(
      "--event_id",
      type=str,
      required=True,
      help=("URL-encoded Base64 ID of the Event"),
  )
  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  event = get_udm_event(
      auth_session,
      args.project_id,
      args.project_instance,
      args.region,
      args.event_id)
  print(json.dumps(event, indent=2))
