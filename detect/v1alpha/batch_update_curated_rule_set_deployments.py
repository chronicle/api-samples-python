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
r"""Executable sample for batch updating curated rule sets deployments.

Sample Commands (run from api_samples_python dir):
    # Modify the script to update the constants that point to deployments.
    python3 -m detect.v1alpha.batch_update_curated_rule_set_deployments \
        -r=<region> -p=<project_id> -i=<instance_id>

API reference:
    https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.curatedRuleSetCategories.curatedRuleSets.curatedRuleSetDeployments/batchUpdate
    https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.curatedRuleSetCategories.curatedRuleSets.curatedRuleSetDeployments#CuratedRuleSetDeployment
"""
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
    proj_region: str,
    proj_id: str,
    proj_instance: str,
) -> Mapping[str, Any]:
  """Batch update curated rule set deployments.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_region: region in which the target project is located
    proj_id: GCP project id or number which the target instance belongs to
    proj_instance: uuid of the instance (with dashes)

  Returns:
    an object with information about the modified deployments

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """

  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      args.region
  )
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"

  # We use "-" in the URL because we provide category and rule_set IDs
  # in the request data.
  url = f"{base_url_with_region}/v1alpha/{parent}/curatedRuleSetCategories/-/curatedRuleSets/-/curatedRuleSetDeployments:batchUpdate"

  # Helper function for making a deployment name. Use this as the
  # curated_rule_set_deployment.name field in the request data below.
  def make_deployment_name(category, rule_set, precision):
    return f"{parent}/curatedRuleSetCategories/{category}/curatedRuleSets/{rule_set}/curatedRuleSetDeployments/{precision}"

  # Note that IDs are hard-coded below, as examples.
  print("\nCategories, rule sets, and precisions are hard-coded as " +
        "examples. Update the script to provide actual IDs.\n"
        )

  # Modify the category/rule_set/precision for each deployment below.
  # Deployment A.
  category_a = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
  rule_set_a = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
  precision_a = "broad"

  # Deployment B.
  category_b = "cccccccc-cccc-cccc-cccc-cccccccccccc"
  rule_set_b = "dddddddd-dddd-dddd-dddd-dddddddddddd"
  precision_b = "precise"

  # Modify the data below to change the behavior of the request.
  # - Add elements to `requests` to batch update multiple deployments
  # - Change the enabled and alerting fields as needed
  # - Change the update_mask to modify only certain properties
  json_data = {
      "parent": f"{parent}/curatedRuleSetCategories/-/curatedRuleSets/-",
      "requests": [
          {
              "curated_rule_set_deployment": {
                  "name": make_deployment_name(
                      category_a,
                      rule_set_a,
                      precision_a,
                  ),
                  "enabled": True,
                  "alerting": False,
              },
              "update_mask": {
                  "paths": ["alerting", "enabled"],
              },
          },
          {
              "curated_rule_set_deployment": {
                  "name": make_deployment_name(
                      category_b,
                      rule_set_b,
                      precision_b,
                  ),
                  "enabled": True,
                  "alerting": True,
              },
              "update_mask": {
                  "paths": ["alerting", "enabled"],
              },
          },
      ],
    }

  # See API reference links at top of this file, for response format.
  response = http_session.request("POST", url, json=json_data)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)

  args = parser.parse_args()
  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES
  )
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  print(
      json.dumps(
          batch_update_curated_rule_set_deployments(
              auth_session,
              args.region,
              args.project_id,
              args.project_instance,
          ),
          indent=2,
      )
  )
