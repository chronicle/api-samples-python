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
r"""Executable and reusable v1alpha API sample for finding asset events in Chronicle.

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacyFindAssetEvents
"""
# pylint: enable=line-too-long

import argparse
import datetime
import json
from typing import Optional

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

DEFAULT_MAX_RESULTS = 10000
MAX_RESULTS_LIMIT = 250000


def find_asset_events(http_session: requests.AuthorizedSession,
                      proj_id: str,
                      proj_instance: str,
                      proj_region: str,
                      asset_indicator: str,
                      start_time: str,
                      end_time: str,
                      reference_time: Optional[str] = None,
                      max_results: Optional[int] = None) -> None:
  """Find asset events in Chronicle using the Legacy Find Asset Events API.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the instance.
    proj_region: region in which the target project is located.
    asset_indicator: JSON str containing the asset indicator to search for.
    start_time: Start time in RFC3339 format (e.g., "2024-01-01T00:00:00Z").
    end_time: End time in RFC3339 format (e.g., "2024-01-02T00:00:00Z").
    reference_time: Optional reference time in RFC3339 format for
      asset aliasing.
    max_results: Optional maximum number of results to return
      (default: 10000, max: 250000).

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
        (response.status_code >= 400).
    ValueError: If the time format is invalid.

  Requires the following IAM permission on the instance resource:
  chronicle.legacies.legacyFindAssetEvents
  """
  # Validate and parse the times to ensure they're in RFC3339 format
  for time_str in [start_time, end_time, reference_time
                  ] if reference_time else [start_time, end_time]:
    try:
      datetime.datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
      if "does not match format" in str(e):
        raise ValueError(f"Time '{time_str}' must be in RFC3339 format "
                         "(e.g., '2024-01-01T00:00:00Z')") from e
      raise

  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable=line-too-long
  instance = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{instance}/legacy:legacyFindAssetEvents"
  # pylint: enable=line-too-long

  # Build query parameters
  params = [
      f"assetIndicator={asset_indicator}", f"timeRange.startTime={start_time}",
      f"timeRange.endTime={end_time}"
  ]

  if reference_time:
    params.append(f"referenceTime={reference_time}")

  if max_results:
    # Ensure max_results is within bounds
    max_results = min(max(1, max_results), MAX_RESULTS_LIMIT)
    params.append(f"maxResults={max_results}")

  url = f"{url}?{'&'.join(params)}"

  response = http_session.request("GET", url)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()

  result = response.json()
  print(json.dumps(result, indent=2))

  if result.get("more_data_available"):
    print("\nWarning: More data is available but was not returned due to "
          "maxResults limit.")

  if result.get("uri"):
    print("\nBackstory UI URLs:")
    for uri in result["uri"]:
      print(f"  {uri}")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument("--asset_indicator",
                      type=str,
                      required=True,
                      help="JSON string containing the asset indicator "
                      "(e.g., '{\"hostname\": \"example.com\"}')")
  parser.add_argument(
      "--start_time",
      type=str,
      required=True,
      help="Start time in RFC3339 format (e.g., '2024-01-01T00:00:00Z')")
  parser.add_argument(
      "--end_time",
      type=str,
      required=True,
      help="End time in RFC3339 format (e.g., '2024-01-02T00:00:00Z')")
  parser.add_argument(
      "--reference_time",
      type=str,
      help="Optional reference time in RFC3339 format for asset aliasing")
  parser.add_argument(
      "--max_results",
      type=int,
      help="Maximum number of results to return "
      f"(default: {DEFAULT_MAX_RESULTS}, max: {MAX_RESULTS_LIMIT})")

  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  find_asset_events(auth_session, args.project_id, args.project_instance,
                    args.region, args.asset_indicator, args.start_time,
                    args.end_time, args.reference_time, args.max_results)
