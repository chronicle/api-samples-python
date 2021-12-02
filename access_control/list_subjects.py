#!/usr/bin/env python3

# Copyright 2021 Google LLC
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
"""Executable and reusable sample for retrieving a list of subjects.

API reference:
https://cloud.google.com/chronicle/docs/reference/rbac-api#listsubjects
"""

import argparse
import json
import sys
from typing import Any, Mapping
from typing import Optional
from typing import Sequence

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def initialize_command_line_args(
    args: Optional[Sequence[str]] = None) -> Optional[argparse.Namespace]:
  """Initializes the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  return parser.parse_args(args)


def list_subjects(
    http_session: requests.AuthorizedSession) -> Sequence[Mapping[str, Any]]:
  """Retrieves list of subjects.

  Args:
    http_session: Authorized session for HTTP requests.

  Returns:
    List of subjects in the form:
    {
      "subjects": [
        {
          "name": "test@test.com",
          "type": "SUBJECT_TYPE_ANALYST",
          "roles": [
            {
              "name": "Test",
              "title": "Test role",
              "description": "The Test role",
              "createTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
              "isDefault": false,
              "permissions": [
                {
                  "name": "Test",
                  "title": "Test permission",
                  "description": "The Test permission",
                  "createTime": "yyyy-mm-ddThh:mm:ss.ssssssZ"
                }
              ]
            }
          ]
        },
        ...
      ]
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/subjects/"
  response = http_session.request("GET", url)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json().get("subjects", [])


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(json.dumps(list_subjects(session), indent=2))
