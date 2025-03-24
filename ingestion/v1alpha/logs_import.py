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
"""API Sample to import logs."""
import argparse
import base64
import datetime
import json
import logging
from typing import Mapping, Any

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def logs_import(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    log_type: str,
    logs_file: str,
    forwarder_id: str) -> Mapping[str, Any]:
  """Imports logs to Chronicle using the GCP CLOUDAUDIT log type.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: Google Cloud project ID.
    proj_instance: Chronicle instance.
    proj_region: Chronicle region.
    log_type: Log type.
    logs_file: File-like object containing the logs to import.
    forwarder_id: UUID4 of the forwarder.

  Returns:
    dict: JSON response from the API.

  Raises:
    requests.HTTPError: If the request fails.
  """
  parent = (f"projects/{proj_id}/"
            f"locations/{proj_region}/"
            f"instances/{proj_instance}/"
            f"logTypes/{log_type}")

  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      proj_region
  )
  url = (f"{base_url_with_region}/v1alpha/{parent}/logs:import")
  logs = logs_file.read()
  # Reset file pointer to beginning in case it needs to be read again
  logs_file.seek(0)
  logs = base64.b64encode(logs.encode("utf-8")).decode("utf-8")
  now = datetime.datetime.now(datetime.timezone.utc).isoformat()
  body = {
      "inline_source": {
          "logs": [
              {
                  "data": logs,
                  "log_entry_time": now,
                  "collection_time": now,
                  "labels": {
                      "forwarder_id": {"value": forwarder_id}
                  }
              }
          ],
          "forwarder": (f"projects/{proj_id}/"
                        f"locations/{proj_region}/"
                        f"instances/{proj_instance}/"
                        f"forwarders/{forwarder_id}")
      }
  }
  response = http_session.request("POST", url, json=body)
  if response.status_code >= 400:
    logging.error("Error response: %s", response.text)
  response.raise_for_status()
  logging.info("Request successful with status code: %d", response.status_code)
  return response.json()


def main():
  """Main entry point for the logs import script."""
  # Configure logging
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  )
  logger = logging.getLogger(__name__)

  parser = argparse.ArgumentParser(description="Import logs to Chronicle.")
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument(
      "--forwarder_id",
      type=str,
      required=True,
      help="UUID4 of the forwarder")
  parser.add_argument(
      "--log_type",
      type=str,
      required=True,
      help="Log type")
  parser.add_argument(
      "--logs_file",
      type=argparse.FileType("r"),
      required=True,
      help="path to a log file (or \"-\" for STDIN)")
  args = parser.parse_args()
  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  try:
    result = logs_import(
        auth_session,
        args.project_id,
        args.project_instance,
        args.region,
        args.log_type,
        args.logs_file,
        args.forwarder_id
    )
    logger.info("Import operation completed successfully")
    print(json.dumps(result, indent=2))
  except Exception as e:  # pylint: disable=broad-except
    logger.error("Import operation failed: %s", str(e))
    return 1
  return 0


if __name__ == "__main__":
  main()
