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
r"""Executable and reusable v1alpha API sample for finding UDM events in Chronicle.

Usage:
  python -m search.v1alpha.udm_events_find \
    --project_id=<PROJECT_ID> \
    --project_instance=<PROJECT_INSTANCE> \
    --region=<REGION> \
    --tokens='["token1", "token2"]'

  # Or using event IDs:
  python -m search.v1alpha.udm_events_find \
    --project_id=<PROJECT_ID> \
    --project_instance=<PROJECT_INSTANCE> \
    --region=<REGION> \
    --event_ids='["id1", "id2"]'

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacyFindUdmEvents
"""
# pylint: enable=line-too-long

import argparse
import json
from typing import List, Optional

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def find_udm_events(http_session: requests.AuthorizedSession,
                    proj_id: str,
                    proj_instance: str,
                    proj_region: str,
                    tokens: Optional[List[str]] = None,
                    event_ids: Optional[List[str]] = None,
                    return_unenriched_data: bool = False,
                    return_all_events_for_log: bool = False) -> None:
  # pylint: disable=line-too-long
  """Find UDM events in Chronicle using the Legacy Find UDM Events API.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    tokens: Optional list of tokens, with each token referring to a group of UDM/Entity events.
    event_ids: Optional list of UDM/Entity event ids that should be returned.
      If both tokens and event_ids are provided, tokens will be discarded.
    return_unenriched_data: Optional boolean to return unenriched data. Default is False.
    return_all_events_for_log: Optional boolean to return all events generated from the ingested log.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.events.batchGet
  """
  # pylint: enable=line-too-long
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable-next=line-too-long
  instance = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{instance}/legacy:legacyFindUdmEvents"

  # Build query parameters
  params = []
  if tokens and not event_ids:  # event_ids take precedence over tokens
    for token in tokens:
      params.append(f"tokens={token}")
  if event_ids:
    for event_id in event_ids:
      params.append(f"ids={event_id}")
  if return_unenriched_data:
    params.append("returnUnenrichedData=true")
  if return_all_events_for_log:
    params.append("returnAllEventsForLog=true")

  if params:
    url = f"{url}?{'&'.join(params)}"

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
  parser.add_argument(
      "--tokens",
      type=str,
      help=
      'JSON string containing a list of tokens (e.g., \'["token1", "token2"]\')'
  )
  parser.add_argument(
      "--event_ids",
      type=str,
      help=
      'JSON string containing a list of event IDs (e.g., \'["id1", "id2"]\')')
  parser.add_argument("--return_unenriched_data",
                      action="store_true",
                      help="Whether to return unenriched data")
  parser.add_argument(
      "--return_all_events_for_log",
      action="store_true",
      help="Whether to return all events generated from the ingested log")

  args = parser.parse_args()

  # Convert JSON strings to lists if provided
  tokens_list = json.loads(args.tokens) if args.tokens else None
  event_ids_list = json.loads(args.event_ids) if args.event_ids else None

  # Validate that at least one of tokens or event_ids is provided
  if not tokens_list and not event_ids_list:
    parser.error("At least one of --tokens or --event_ids must be provided")

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  find_udm_events(auth_session, args.project_id, args.project_instance,
                  args.region, tokens_list, event_ids_list,
                  args.return_unenriched_data, args.return_all_events_for_log)
