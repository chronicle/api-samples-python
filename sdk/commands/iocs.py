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
"""Chronicle IoCs API commands."""

import json

import click
from common import chronicle_auth

from iocs.v1alpha import batch_get_iocs
from iocs.v1alpha import get_ioc
from iocs.v1alpha import get_ioc_state
from sdk.commands.common import add_common_options

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


@click.group()
def iocs():
  """IoCs API commands."""
  pass


@iocs.command("batch-get")
@add_common_options
@click.option(
    "--ioc-values",
    required=True,
    help="JSON array of IoC values to retrieve.",
)
@click.option(
    "--ioc-type",
    type=click.Choice([
        "IOC_TYPE_UNSPECIFIED",
        "DOMAIN",
        "IP",
        "FILE_HASH",
        "URL",
        "USER_EMAIL",
        "MUTEX",
        "FILE_HASH_MD5",
        "FILE_HASH_SHA1",
        "FILE_HASH_SHA256",
        "IOC_TYPE_RESOURCE",
    ]),
    required=True,
    help="Type of IoCs being requested.",
)
def batch_get_iocs_cmd(credentials_file, project_id, project_instance, region,
                       ioc_values, ioc_type):
  """Get multiple IoCs by their values."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )

  ioc_values_list = json.loads(ioc_values)

  result = batch_get_iocs.batch_get_iocs(
      auth_session,
      project_id,
      project_instance,
      region,
      ioc_values_list,
      ioc_type,
  )
  print(json.dumps(result, indent=2))


@iocs.command("get")
@add_common_options
@click.option(
    "--ioc-value",
    required=True,
    help="Value of the IoC to retrieve.",
)
@click.option(
    "--ioc-type",
    type=click.Choice([
        "IOC_TYPE_UNSPECIFIED",
        "DOMAIN",
        "IP",
        "FILE_HASH",
        "URL",
        "USER_EMAIL",
        "MUTEX",
        "FILE_HASH_MD5",
        "FILE_HASH_SHA1",
        "FILE_HASH_SHA256",
        "IOC_TYPE_RESOURCE",
    ]),
    required=True,
    help="Type of IoC being requested.",
)
def get_ioc_cmd(credentials_file, project_id, project_instance, region,
                ioc_value, ioc_type):
  """Get a single IoC by its value."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )

  result = get_ioc.get_ioc(
      auth_session,
      project_id,
      project_instance,
      region,
      ioc_value,
      ioc_type,
  )
  print(json.dumps(result, indent=2))


@iocs.command("get-state")
@add_common_options
@click.option(
    "--ioc-value",
    required=True,
    help="Value of the IoC to get state for.",
)
@click.option(
    "--ioc-type",
    type=click.Choice([
        "IOC_TYPE_UNSPECIFIED", "DOMAIN", "IP", "FILE_HASH", "URL",
        "USER_EMAIL", "MUTEX", "FILE_HASH_MD5", "FILE_HASH_SHA1",
        "FILE_HASH_SHA256", "IOC_TYPE_RESOURCE"
    ]),
    required=True,
    help="Type of IoC being requested.",
)
def get_ioc_state_cmd(credentials_file, project_id, project_instance, region,
                      ioc_value, ioc_type):
  """Get the state of an IoC by its value."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )

  result = get_ioc_state.get_ioc_state(
      auth_session,
      project_id,
      project_instance,
      region,
      ioc_value,
      ioc_type,
  )
  print(json.dumps(result, indent=2))
