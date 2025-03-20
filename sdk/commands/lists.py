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
"""Chronicle Lists API commands."""

import json

import click
from common import chronicle_auth

from lists.v1alpha import create_list
from lists.v1alpha import get_list
from lists.v1alpha import patch_list
from sdk.commands.common import add_common_options

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


@click.group()
def lists():
  """Lists API commands."""
  pass


@lists.command("create")
@add_common_options
@click.option(
    "--name",
    required=True,
    help="Name of the list to create.",
)
@click.option(
    "--description",
    help="Description of the list.",
)
@click.option(
    "--lines",
    required=True,
    help="JSON array of strings to add to the list.",
)
def create_list_cmd(credentials_file, project_id, project_instance, region,
                    name, description, lines):
  """Create a new list."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = create_list.create_list(
      auth_session,
      project_id,
      project_instance,
      region,
      name,
      description,
      lines,
  )
  print(json.dumps(result, indent=2))


@lists.command("get")
@add_common_options
@click.option(
    "--list-id",
    required=True,
    help="ID of the list to retrieve.",
)
def get_list_cmd(credentials_file, project_id, project_instance, region,
                 list_id):
  """Get a list by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = get_list.get_list(
      auth_session,
      project_id,
      project_instance,
      region,
      list_id,
  )
  print(json.dumps(result, indent=2))


@lists.command("patch")
@add_common_options
@click.option(
    "--list-id",
    required=True,
    help="ID of the list to update.",
)
@click.option(
    "--description",
    help="New description for the list.",
)
@click.option(
    "--lines-to-add",
    help="JSON array of strings to add to the list.",
)
@click.option(
    "--lines-to-remove",
    help="JSON array of strings to remove from the list.",
)
def patch_list_cmd(credentials_file, project_id, project_instance, region,
                   list_id, description, lines_to_add, lines_to_remove):
  """Update an existing list."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = patch_list.patch_list(
      auth_session,
      project_id,
      project_instance,
      region,
      list_id,
      description,
      lines_to_add,
      lines_to_remove,
  )
  print(json.dumps(result, indent=2))






