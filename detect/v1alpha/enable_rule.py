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
r"""Executable and reusable v1alpha API sample for enabling a detection rule.

Usage:
  python -m detect.v1alpha.enable_rule \
    --project_id=<PROJECT_ID> \
    --project_instance=<PROJECT_INSTANCE> \
    --region=<REGION> \
    --rule_id=ru_<UUID>

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.rules/updateDeployment
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/RuleDeployment
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


def enable_rule(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    rule_id: str,
) -> Mapping[str, Any]:
  """Enables a detection rule.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    rule_id: Unique ID of the detection rule to enable
      (in the format "ru_<UUID>").

  Returns:
    Dictionary containing the rule's deployment information.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).

  Requires the following IAM permission on the parent resource:
  chronicle.rules.updateDeployment
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/rules/{rule_id}/deployment"

  body = {
      "enabled": True,  # Set to False to disable the rule
  }
  params = {"update_mask": "enabled"}

  response = http_session.request("PATCH", url, params=params, json=body)
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
  parser.add_argument("--rule_id",
                      type=str,
                      required=True,
                      help='ID of rule to enable (format: "ru_<UUID>")')

  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(args.credentials_file,
                                                        SCOPES)
  result = enable_rule(auth_session, args.project_id, args.project_instance,
                       args.region, args.rule_id)
  print(json.dumps(result, indent=2))
