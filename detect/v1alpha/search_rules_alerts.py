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
r"""Executable sample for getting a list of generated alerts.

Sample Command (run from api_samples_python dir):
    python3 -m detect.v1alpha.search_rules_alerts \
      --region=$REGION \
      --project_id=$PROJECT_ID \
      --project_instance=$PROJECT_INSTANCE \
      --credentials_file=$CREDENTIALS_FILE \
      --start_time="2024-11-11T13:37:32Z" \
      --start_time="2024-11-19T13:37:32Z" \
      --rule_status=ALL \
      --page_size=10

API reference:
    https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacySearchRulesAlerts
"""
import argparse
import datetime
import json
from typing import Any, Mapping
from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

RULE_STATUS = (
    "ACTIVE",
    "ARCHIVED",
    "ALL",
)


def search_rules_alerts(
    http_session: requests.AuthorizedSession,
    proj_region: str,
    proj_id: str,
    proj_instance: str,
    start_time: str,
    end_time: str,
    rule_status: str | None = None,
    page_size: int | None = None,
) -> Mapping[str, Any]:
  """...

  Args:
    http_session: Authorized session for HTTP requests.
    proj_region: region in which the target project is located
    proj_id: GCP project id or number which the target instance belongs to
    proj_instance: uuid of the instance (with dashes)
    start_time: A timestamp in RFC3339 UTC "Zulu" format, with nanosecond
     resolution and up to nine fractional digits.
    end_time: A timestamp in RFC3339 UTC "Zulu" format, with nanosecond
     resolution and up to nine fractional digits.
    rule_status: if provided, limit the alerts to ACTIVE | ARCHIVED | ALL 
    page_size: if provided, limit the number of alerts returned

  Returns:
    a list of detections

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, args.region
  )
  # pylint: disable-next=line-too-long
  instance = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{instance}/legacy:legacySearchRulesAlerts"
  params = {"timeRange.start_time": start_time, "timeRange.end_time": end_time}
  if rule_status:
    if rule_status not in RULE_STATUS:
      raise ValueError(
          f"rule_status must be one of {RULE_STATUS}, got {rule_status}"
      )
    params["ruleStatus"] = rule_status
  if page_size:
    params["maxNumAlertsToReturn"] = page_size

  # See API reference links at top of this file, for response format.
  response = http_session.request("GET", url, params=params)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  now = datetime.datetime.now()
  yesterday = now - datetime.timedelta(hours=24)
  # Format the datetime object into the desired string
  start_time_string = yesterday.strftime("%Y-%m-%dT%H:%M:%SZ")

  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  parser.add_argument(
      "--start_time",
      type=str,
      required=False,
      default=start_time_string,
  )
  parser.add_argument(
      "--end_time",
      type=str,
      required=False,
      default=now.strftime("%Y-%m-%dT%H:%M:%SZ"),
  )
  parser.add_argument(
      "--rule_status",
      choices=RULE_STATUS,
      required=False,
      default="ALL",
  )
  parser.add_argument(
      "--page_size",
      type=int,
      required=False,
      default=10,
  )
  args = parser.parse_args()
  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file, SCOPES
  )
  print(
      json.dumps(
          search_rules_alerts(
              auth_session,
              args.region,
              args.project_id,
              args.project_instance,
              args.start_time,
              args.end_time,
              args.rule_status,
              args.page_size,
          ),
          indent=2,
      )
  )
