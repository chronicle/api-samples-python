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
r"""Executable and reusable v1alpha API sample for creating a retrohunt.

Usage:
  python -m detect.v1alpha.create_retrohunt \
    --project_id=<PROJECT_ID> \
    --project_instance=<PROJECT_INSTANCE> \
    --region=<REGION> \
    --rule_id=ru_<UUID> \
    --start_time=2023-10-02T18:00:00Z \
    --end_time=2023-10-02T20:00:00Z

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.rules.retrohunts/create
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.operations#Operation
"""
# pylint: enable=line-too-long

import argparse
import datetime
import json
from typing import Any, Mapping

from common import chronicle_auth
from common import datetime_converter
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def create_retrohunt(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    rule_id: str,
    start_time: datetime.datetime,
    end_time: datetime.datetime,
) -> Mapping[str, Any]:
  """Creates a retrohunt to run a detection rule over historical data.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    rule_id: Unique ID of the detection rule to run (in the format "ru_<UUID>").
    start_time: Start time of the event time range for the retrohunt.
    end_time: End time of the event time range for the retrohunt.

  Returns:
    Dictionary containing the Operation resource for the retrohunt.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.retrohunts.create
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/rules/{rule_id}/retrohunts"
  # pylint: enable=line-too-long

  body = {
      "process_interval": {
          "start_time": datetime_converter.strftime(start_time),
          "end_time": datetime_converter.strftime(end_time),
      },
  }

  response = http_session.request("POST", url, json=body)
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
      "--rule_id",
      type=str,
      required=True,
      help='ID of rule to create retrohunt for (format: "ru_<UUID>")')
  parser.add_argument("--start_time",
                      type=datetime_converter.iso8601_datetime_utc,
                      required=True,
                      help="Start time in UTC (format: yyyy-mm-ddThh:mm:ssZ)")
  parser.add_argument("--end_time",
                      type=datetime_converter.iso8601_datetime_utc,
                      required=True,
                      help="End time in UTC (format: yyyy-mm-ddThh:mm:ssZ)")

  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(args.credentials_file,
                                                        SCOPES)
  result = create_retrohunt(auth_session, args.project_id,
                            args.project_instance, args.region, args.rule_id,
                            args.start_time, args.end_time)
  print(json.dumps(result, indent=2))
