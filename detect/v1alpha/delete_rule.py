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
r"""Executable sample for deleting a rule.

Sample Commands (run from api_samples_python dir):
    python3 -m detect.v1alpha.delete_rule -r=<region> \
        -p=<project_id> -i=<instance_id> \
        -rid=<rule_id>

API reference:
    https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.rules/delete
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


def delete_rule(
    http_session: requests.AuthorizedSession,
    proj_region: str,
    proj_id: str,
    proj_instance: str,
    rule_id: str,
) -> Mapping[str, Any]:
  """Deletes a rule.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_region: region in which the target project is located
    proj_id: GCP project id or number which the target instance belongs to
    proj_instance: uuid of the instance (with dashes)
    rule_id: Unique ID of the detection rule to retrieve ("ru_<UUID>").

  Returns:
    an empty response

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
  url = f"{base_url_with_region}/v1alpha/{parent}/rules/{rule_id}"

  # See API reference links at top of this file, for response format.
  response = http_session.request("DELETE", url)
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
  parser.add_argument(
      "-rid",
      "--rule_id",
      type=str,
      required=True,
      help='ID of rule to be deleted. In the form of "ru_<UUID>"',
  )
  args = parser.parse_args()
  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES
  )
  print(
      json.dumps(
          delete_rule(
              auth_session,
              args.region,
              args.project_id,
              args.project_instance,
              args.rule_id,
          ),
          indent=2,
      )
  )
