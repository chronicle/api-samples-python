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
"""Executable and reusable sample for retrieving a list of entity risk scores."""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions


CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"


def list_entity_risk_scores(
    http_session: requests.AuthorizedSession,
    region: str,
    project: str,
    instance: str,
    filters: str = "",
    order_by: str = "",
    page_size: int = 0,
    page_token: str = "",
) -> Mapping[str, Any]:
  """Retrieves a list of entity risk scores.

  Args:
    http_session: Authorized session for HTTP requests.
    region: region in which the target project is located.
    project: GCP project id or number which the target instance belongs to.
    instance: uuid of the instance whose feeds are being listed (with dashes).
    filters: Filters to be applied. Please see API definition for usage.
    order_by: Ordering of Entity Risk Scores.
    page_size: The maximum number of Entity Risk Scores to return.
    page_token: A page token, received from a previous call. Used to retrieve
      subsequent pages.

  Returns:
    JSON Object containing entity_risk_scores as well as other information about
    the scores.
  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url_region = "us" if region == "govcloud-us" else region
  url = f"{CHRONICLE_API_BASE_URL}/v1alpha/projects/{project}/locations/{url_region}/instances/{instance}/entityRiskScores:query"
  params_list = [
      ("filter", filters),
      ("order_by", order_by),
      ("page_size", page_size),
      ("page_token", page_token),
  ]
  params = {k: v for k, v in params_list if v}

  response = http_session.request("GET", url, params=params)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-i",
      "--instance",
      type=str,
      required=True,
      help="instance to list feeds for",
  )
  parser.add_argument(
      "-p",
      "--project",
      type=str,
      required=True,
      help="project to list feeds for",
  )
  parser.add_argument(
      "-f",
      "--filter",
      type=str,
      required=False,
      help=(
          "Filter to be applied over multiple entity risk score fields. Please"
          " see API definition for usage"
      ),
  )
  parser.add_argument(
      "-o",
      "--order_by",
      type=str,
      required=False,
      help="Ordering of Entity Risk Scores",
  )
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of results to return",
  )
  parser.add_argument(
      "-t",
      "--page_token",
      type=str,
      required=False,
      help="page token from a previous call used for pagination",
  )

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      scopes=["https://www.googleapis.com/auth/cloud-platform"],
  )
  print(
      json.dumps(
          list_entity_risk_scores(
              session,
              args.region,
              args.project,
              args.instance,
              args.filter,
              args.order_by,
              args.page_size,
              args.page_token,
          ),
          indent=2,
      )
  )
