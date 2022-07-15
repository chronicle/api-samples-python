#!/usr/bin/env python3

# Copyright 2022 Google LLC
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
"""Executable and reusable sample for creating a Datatap.

API reference:
https://cloud.google.com/chronicle/docs/preview/datatap-config/datatapconfig-api?hl=en#create
"""

import argparse
import json
import sys
from typing import Any, Mapping
from typing import Optional
from typing import Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-n", "--name", type=str, required=True, help="display name")
  parser.add_argument(
      "-t",
      "--topic",
      type=str,
      required=True,
      help="Topic in format projects/<project_id>/topics/<topicId>")
  parser.add_argument(
      "-f",
      "--filter",
      type=str,
      required=True,
      help="filter Type, Options: ALL_UDM_EVENTS/ALERT_UDM_EVENTS")
  parser.add_argument(
      "-sf",
      "--serialization_format",
      type=str,
      required=False,
      help="serialization Format, Options : MARSHALLED_PROTO/JSON")

  # Sanity check for the filter type.
  parsed_args = parser.parse_args(args)
  if parsed_args.filter not in ("ALL_UDM_EVENTS", "ALERT_UDM_EVENTS"):
    print("Error: filter type must be <ALL_UDM_EVENTS | ALERT_UDM_EVENTS>")
    return None

  return parser.parse_args(args)


def create_datatap(http_session: requests.AuthorizedSession, name: str,
                   topic: str,
                   filter_type: str,
                   serialization_format: str,) -> Mapping[str, Sequence[Any]]:
  """Creates a datatap.

  Args:
    http_session: Authorized session for HTTP requests.
    name: name of the config to be created.
    topic: topicId of the pubsub topic where events should be published.
    filter_type: The filter type to filter events, e.g., ALL_UDM_EVENTS
      or ALERT_UDM_EVENTS.
    serialization_format: The serialization format in which events are
      needed, e.g., MARSHALLED_PROTO or JSON.

  Returns:
    Information about the newly created data in the form:
    {
      "customerId": "cccccccc-cccc-cccc-cccc-cccccccccccc",
      "tapId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
      "displayName": "tap1",
      "filter": "ALL_UDM_EVENTS",
      "serializationFormat": "MARSHALLED_PROTO"
      "cloudPubsubSink": {
        "topic": "projects/sample-project/topics/sample-topic",
      }
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/dataTaps"

  body = {
      "displayName": name,
      "cloudPubsubSink": {
          "topic": topic,
      },
      "filter": filter_type,
      "serializationFormat": serialization_format
  }

  response = http_session.request("POST", url, json=body)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(
      json.dumps(
          create_datatap(session, cli.name, cli.topic, cli.filter,
                         cli.serialization_format),
          indent=2))
