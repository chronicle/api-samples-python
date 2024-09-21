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
# pylint: disable=line-too-long
"""Executable and reusable sample for creating a Reference List.

 Requires the following IAM permission on the parent resource:
 chronicle.referenceLists.create

 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists/create
"""
# pylint: enable=line-too-long

import argparse
from typing import Any, Dict, Optional, Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]
PREFIX = "REFERENCE_LIST_SYNTAX_TYPE_"
SYNTAX_TYPE_ENUM = [
    f"{PREFIX}UNSPECIFIED",  # Defaults to ..._PLAIN_TEXT_STRING.
    f"{PREFIX}PLAIN_TEXT_STRING",  # List contains plain text patterns.
    f"{PREFIX}REGEX",  # List contains only Regular Expression patterns.
    f"{PREFIX}CIDR",  # List contains only CIDR patterns.
]


def create_list(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    name: str,
    description: str,
    content_lines: Sequence[str],
    content_type: str,
    scope_name: Optional[str] | None = None,
) -> Dict[str, Any]:
  """Creates a list.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    name: Unique name for the list.
    description: Description of the list.
    content_lines: Array containing each line of the list's content.
    content_type: Type of list content, indicating how to interpret this list.
    scope_name: (Optional) Data RBAC scope name for the list.
  Returns:
    Dictionary representation of the created Reference List.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  # pylint: disable=line-too-long
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      proj_region
  )
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/referenceLists"
  # pylint: enable=line-too-long

  # entries are list like [{"value": <string>}, ...]
  # pylint: disable-next=line-too-long
  # https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#resource:-referencelist
  entries = []
  for content_line in content_lines:
    entries.append({"value": content_line.strip()})

  body = {
      "name": name,
      "description": description,
      "entries": entries,
      "syntax_type": content_type,
  }
  if scope_name:
    body["scope_info"] = {
        "referenceListScope": {
            "scopeNames": [
                f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}/dataAccessScopes/{scope_name}"
            ]
        }
    }
  else:
    body["scope_info"] = None
  params = {"referenceListId": name}
  response = http_session.request("POST", url, params=params, json=body)
  # Expected server response:
  # ['name', 'displayName', 'revisionCreateTime', 'description',
  #  'entries', 'syntaxType'])
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-n", "--name", type=str, required=True, help="unique name for the list"
  )
  parser.add_argument(
      "-d",
      "--description",
      type=str,
      required=True,
      help="description of the list",
  )
  parser.add_argument(
      "-s", "--scope_name", type=str, help="data RBAC scope name for the list"
  )
  parser.add_argument(
      "-t",
      "--syntax_type",
      type=str,
      required=False,
      default="REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING",
      choices=SYNTAX_TYPE_ENUM,
      # pylint: disable-next=line-too-long
      help="syntax type of the list, used for validation (default: REFERENCE_LIST_SYNTAX_TYPE_PLAIN_TEXT_STRING)",
  )
  parser.add_argument(
      "-f",
      "--list_file",
      type=argparse.FileType("r"),
      required=True,
      # File example:
      #   python3 -m lists.v1alpha.create_list <other args> -f <path>
      # STDIN example:
      #   cat <path> | python3 -m lists.v1alpha.create_list <other args> -f -
      help="path of a file containing the list content, or - for STDIN",
  )
  args = parser.parse_args()

  # pylint: disable-next=line-too-long
  auth_session = chronicle_auth.initialize_http_session(args.credentials_file, SCOPES)
  response_json = create_list(
      auth_session,
      args.project_id,
      args.project_instance,
      args.region,
      args.name,
      args.description,
      args.list_file.read().splitlines(),
      args.syntax_type,
      args.scope_name,
  )
  print("New list created successfully, at "
        f"{response_json.get('revisionCreateTime')}")
