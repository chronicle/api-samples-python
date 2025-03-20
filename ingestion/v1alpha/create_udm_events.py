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
r"""Executable and reusable sample for ingesting events in UDM format.

 Usage:
 python3 -m ingestion.v1alpha.create_udm_events \
   --project_instance $PROJECT_INSTANCE \
   --project_id $PROJECT_ID \
   --json_events_file=./ingestion/example_input/sample_udm_events.json

 API reference:
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/import
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/import#EventsInlineSource
 https://cloud.google.com/chronicle/docs/reference/udm-field-list
 https://cloud.google.com/chronicle/docs/unified-data-model/udm-usage
"""

import argparse
import json

from google.auth.transport import requests

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def create_udm_events(
    http_session: requests.AuthorizedSession, json_events: str
) -> None:
  """Sends a collection of UDM events to the Google SecOps backend for ingestion.

  A Unified Data Model (UDM) event is a structured representation of an event
  regardless of the log source.

  Args:
    http_session: Authorized session for HTTP requests.
    json_events: A collection of UDM events in (serialized) JSON format.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.events.import

  POST https://chronicle.googleapis.com/v1alpha/{parent}/events:import

  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.events/import
  """

  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      args.region
  )
  # pylint: disable-next=line-too-long
  parent = f"projects/{args.project_id}/locations/{args.region}/instances/{args.project_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/events:import"
  body = {"inline_source": {"events": [{"udm": json.loads(json_events)[0],}]}}

  response = http_session.request("POST", url, json=body)
  print(response)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return None


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument(
      "--json_events_file",
      type=argparse.FileType("r"),
      required=True,
      help=(
          "path to a file containing a list of UDM events in json format"
      ),
  )
  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  create_udm_events(auth_session, args.json_events_file.read())
