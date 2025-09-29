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
"""Chronicle API Command Line Interface.

This module provides a unified CLI for interacting with Chronicle APIs.
"""

import click

from sdk.commands import detect
from sdk.commands import ingestion
from sdk.commands import iocs
from sdk.commands import lists
from sdk.commands import search


def add_common_options(func):
  """Add common options to a command."""
  func = click.option(
      "--credentials-file",
      required=True,
      help="Path to service account credentials file.",
  )(func)
  func = click.option(
      "--project-id",
      required=True,
      help="GCP project id or number to which the target instance belongs.",
  )(func)
  func = click.option(
      "--project-instance",
      required=True,
      help="Customer ID (uuid with dashes) for the Chronicle instance.",
  )(func)
  func = click.option(
      "--region",
      required=True,
      help="Region in which the target project is located.",
  )(func)
  return func


@click.group()
def cli():
  """Chronicle API Command Line Interface.

  This CLI provides access to Chronicle's detection, ingestion, IoCs,
  search, and lists APIs.
  """
  pass


# Add command groups
cli.add_command(detect.detect)
cli.add_command(ingestion.ingestion)
cli.add_command(iocs.iocs)
cli.add_command(lists.lists)
cli.add_command(search.search)

if __name__ == "__main__":
  cli()
