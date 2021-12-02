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
"""Executable and reusable sample for creating a subject.

A subject can be an analyst or an Identity Provider (IdP) group.

API reference:
https://cloud.google.com/chronicle/docs/reference/rbac-api#createsubject
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
  """Initializes and checks all the command-line arguments."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-n", "--name", type=str, required=True, help="subject ID")
  parser.add_argument(
      "-t", "--type", type=str, required=True, help="subject type")
  parser.add_argument(
      "-rs",
      "--roles",
      type=str,
      required=True,
      help=("the role(s) the created subject must have"))

  # No need for a sanity check for the subject name and roles because these
  # arguments convert the provided input into strings and accept a wide range
  # of values. If the subject name isn't passed in, the error will be thrown
  # from the argparse library.

  # Sanity check for the subject type.
  parsed_args = parser.parse_args(args)
  if parsed_args.type not in ("SUBJECT_TYPE_ANALYST", "SUBJECT_TYPE_IDP_GROUP"):
    print("Error: subject type must be SUBJECT_TYPE_<ANALYST|IDP_GROUP>")
    return None

  return parser.parse_args(args)


def create_subject(http_session: requests.AuthorizedSession, name: str,
                   subject_type: str,
                   roles: Sequence[str]) -> Mapping[str, Sequence[Any]]:
  """Creates a subject.

  Args:
    http_session: Authorized session for HTTP requests.
    name: The ID of the subject to be created.
    subject_type: The type of the subject, e.g., SUBJECT_TYPE_ANALYST or
      SUBJECT_TYPE_IDP_GROUP.
    roles: The role(s) the created subject must have.

  Returns:
    Information about the newly created subject in the form:
    {
      "subject": {
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
                "createTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
              },
              ...
            ]
          },
          ...
        ]
      }
    }

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v1/subjects/"

  body = {
      "name": name,
      "type": subject_type,
      "roles": [{"name": role} for role in roles],
  }
  response = http_session.request("POST", url, json=body)

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  cli = initialize_command_line_args()
  if not cli:
    sys.exit(1)  # A sanity check failed.

  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, cli.region)
  session = chronicle_auth.initialize_http_session(cli.credentials_file)
  print(
      json.dumps(
          create_subject(session, cli.name, cli.type, cli.roles.split(",")),
          indent=2))
