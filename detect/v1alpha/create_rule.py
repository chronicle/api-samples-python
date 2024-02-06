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
r"""Executable and reusable sample for creating a detection rule.

 HTTP request
 POST https://chronicle.googleapis.com/v1alpha/{parent}/rules

 python3 -m detect.v1alpha.create_rule \
   --project_instance $project_instance \
   --project_id $PROJECT_ID \
   --rule_file=./ip_in_abuseipdb_blocklist.yaral

 Requires the following IAM permission on the parent resource:
 chronicle.rules.create

 API reference:
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.rules/create
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.rules#Rule
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def create_rule(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    rule_file_path: str,
) -> Mapping[str, Any]:
  """Creates a new detection rule to find matches in logs.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    rule_file_path: Content of the new detection rule, used to evaluate logs.

  Returns:
    New detection rule.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"https://{proj_region}-chronicle.googleapis.com/v1alpha/{parent}/rules"
  body = {
      "text": rule_file_path.read(),
  }
  response = http_session.request("POST", url, json=body)
  # Expected server response:
  # {
  #   # pylint: disable=line-too-long
  #   "name": "projects/{project}/locations/{location}/instances/{instance}/rules/{rule_id}",
  #   "revisionId": "v_{10_digits}_{9_digits}",
  #   "displayName": "{rule_name}",
  #   "text": "{rule_content}",
  #   "author": str,
  #   "severity": {
  #     "displayName": str
  #   },
  #   "metadata": {
  #     "{key_1}": "{value_1}",
  #     ...
  #   },
  #   "createTime": "yyyy-MM-ddThh:mm:ss.ssssssZ",
  #   "revisionCreateTime": "yyyy-MM-ddThh:mm:ss.ssssssZ"
  #   "compilationState": "SUCCEEDED",
  #   "type": "{{SINGLE,MULTI}_EVENT,RULE_TYPE_UNSPECIFIED}",
  #   "referenceLists": [str],
  #   "allowedRunFrequencies": [
  #     str,
  #     ...
  #   ],
  #   "etag": str
  # }
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
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: python3 create_rule.py -f <path>
      # STDIN example: cat rule.txt | python3 create_rule.py -f -
      help="path of a file with the desired rule's content, or - for STDIN",
  )
  args = parser.parse_args()

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES
  )
  new_rule = create_rule(auth_session,
                         args.project_id,
                         args.project_instance,
                         args.region,
                         args.rule_file)
  print(json.dumps(new_rule, indent=2))
