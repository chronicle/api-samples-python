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
r"""Executable and reusable v1alpha API sample for batch updating curated rule set deployments.

Usage:
  python -m detect.v1alpha.batch_update_curated_rule_set_deployments \
    --project_id=<PROJECT_ID> \
    --project_instance=<PROJECT_INSTANCE> \
    --region=<REGION>

  # The script contains example category/rule_set/precision IDs that need to be updated:
  # Category A: aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa
  # Rule Set A: bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb
  # Precision A: broad
  #
  # Category B: cccccccc-cccc-cccc-cccc-cccccccccccc
  # Rule Set B: dddddddd-dddd-dddd-dddd-dddddddddddd
  # Precision B: precise

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.curatedRuleSetCategories.curatedRuleSets.curatedRuleSetDeployments/batchUpdate
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.curatedRuleSetCategories.curatedRuleSets.curatedRuleSetDeployments#CuratedRuleSetDeployment
"""
# pylint: enable=line-too-long

import argparse
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


def batch_update_curated_rule_set_deployments(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
) -> Mapping[str, Any]:
  """Batch updates multiple curated rule set deployments.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.

  Returns:
    Dictionary containing information about the modified deployments.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.curatedRuleSetDeployments.update
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"

  # We use "-" in the URL because we provide category and rule_set IDs
  # in the request data
  # pylint: disable-next=line-too-long
  url = f"{base_url_with_region}/v1alpha/{parent}/curatedRuleSetCategories/-/curatedRuleSets/-/curatedRuleSetDeployments:batchUpdate"

  def make_deployment_name(category: str, rule_set: str, precision: str) -> str:
    """Helper function to create a deployment name."""
    # pylint: disable-next=line-too-long
    return f"{parent}/curatedRuleSetCategories/{category}/curatedRuleSets/{rule_set}/curatedRuleSetDeployments/{precision}"

  # Example deployment configurations - update these with actual IDs
  # Deployment A
  category_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
  rule_set_a = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
  precision_a = "broad"

  # Deployment B
  category_b = "cccccccc-cccc-cccc-cccc-cccccccccccc"
  rule_set_b = "dddddddd-dddd-dddd-dddd-dddddddddddd"
  precision_b = "precise"

  print("\nNOTE: Using example category/rule_set/precision IDs.")
  print("Please update the script with actual IDs before use.\n")

  json_data = {
      "parent":
          f"{parent}/curatedRuleSetCategories/-/curatedRuleSets/-",
      "requests": [
          {
              "curated_rule_set_deployment": {
                  "name":
                      make_deployment_name(
                          category_a,
                          rule_set_a,
                          precision_a,
                      ),
                  "enabled":
                      True,
                  "alerting":
                      False,
              },
              "update_mask": {
                  "paths": ["alerting", "enabled"],
              },
          },
          {
              "curated_rule_set_deployment": {
                  "name":
                      make_deployment_name(
                          category_b,
                          rule_set_b,
                          precision_b,
                      ),
                  "enabled":
                      True,
                  "alerting":
                      True,
              },
              "update_mask": {
                  "paths": ["alerting", "enabled"],
              },
          },
      ],
  }

  response = http_session.request("POST", url, json=json_data)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()

  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_id.add_argument_project_id(parser)
  project_instance.add_argument_project_instance(parser)
  regions.add_argument_region(parser)

  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(args.credentials_file,
                                                        SCOPES)
  result = batch_update_curated_rule_set_deployments(auth_session,
                                                     args.project_id,
                                                     args.project_instance,
                                                     args.region)
  print(json.dumps(result, indent=2))
