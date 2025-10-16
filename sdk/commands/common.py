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
"""Common utilities for CLI commands."""

import functools
import os

import click
from dotenv import load_dotenv


def get_env_value(key, default=None):
  """Gets value from environment variable with Chronicle prefix.

  Args:
    key: The environment variable key (without CHRONICLE_ prefix).
    default: Default value if environment variable is not set.

  Returns:
    The value of the environment variable or the default value.
  """
  return os.getenv(f"CHRONICLE_{key}", default)


def add_common_options(func):
  """Adds common CLI options to a command.

  Adds standard Chronicle CLI options for region, project instance, project ID,
  credentials file, and environment file. Values can be provided via command
  line arguments or environment variables.

  Args:
    func: The function to wrap with common options.

  Returns:
    A decorated function that includes common Chronicle CLI options.
  """

  # Add CLI options first
  @click.option(
      "--region",
      required=False,
      help="Region in which the target project is located. Can also be set "
      "via CHRONICLE_REGION env var.",
  )
  @click.option(
      "--project-instance",
      required=False,
      help="Customer ID (uuid with dashes) for the Chronicle instance. "
      "Can also be set via CHRONICLE_INSTANCE env var.",
  )
  @click.option(
      "--project-id",
      required=False,
      help="GCP project id or number. Can also be set via CHRONICLE_PROJECT_ID "
      "env var.",
  )
  @click.option(
      "--credentials-file",
      required=False,
      help="Path to service account credentials file. Can also be set via "
      "CHRONICLE_CREDENTIALS_FILE env var.",
  )
  @click.option(
      "--env-file",
      required=False,
      help="Path to .env file containing configuration variables.",
  )
  @functools.wraps(func)
  def wrapper(*args, **kwargs):
    # Load environment variables from .env file
    env_file = kwargs.pop("env_file", None)
    if env_file:
      load_dotenv(env_file)
    else:
      # Look for .env in the current working directory
      cwd_env = os.path.join(os.getcwd(), ".env")
      load_dotenv(cwd_env)

    # Now validate required options
    missing = []
    # pylint: disable=line-too-long
    if not kwargs.get("credentials_file") and not get_env_value(
        "CREDENTIALS_FILE"):
      # pylint: enable=line-too-long
      missing.append("credentials-file (or CHRONICLE_CREDENTIALS_FILE)")
    if not kwargs.get("project_id") and not get_env_value("PROJECT_ID"):
      missing.append("project-id (or CHRONICLE_PROJECT_ID)")
    if not kwargs.get("project_instance") and not get_env_value("INSTANCE"):
      missing.append("project-instance (or CHRONICLE_INSTANCE)")
    if not kwargs.get("region") and not get_env_value("REGION"):
      missing.append("region (or CHRONICLE_REGION)")

    if missing:
      raise click.UsageError(
          f"Missing required options: {', '.join(missing)}\n"
          "These can be provided via command line options or environment "
          "variables.")

    # If options not provided via CLI, get from environment
    if not kwargs.get("credentials_file"):
      kwargs["credentials_file"] = get_env_value("CREDENTIALS_FILE")
    if not kwargs.get("project_id"):
      kwargs["project_id"] = get_env_value("PROJECT_ID")
    if not kwargs.get("project_instance"):
      kwargs["project_instance"] = get_env_value("INSTANCE")
    if not kwargs.get("region"):
      kwargs["region"] = get_env_value("REGION")

    return func(*args, **kwargs)

  return wrapper
