#!/usr/bin/env python3

import argparse
import base64
import datetime
import json
import logging

from google.auth.transport import requests

from common import chronicle_auth
from common import project_instance
from common import project_id
from common import regions

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


def logs_import(http_session: requests.AuthorizedSession, logs_file) -> dict:
  log_type = "GCP_CLOUDAUDIT"
  parent = f"projects/{args.project_id}/" \
           f"locations/{args.region}/" \
           f"instances/{args.project_instance}/" \
           f"logTypes/{log_type}"
  url = f"https://{args.region}-chronicle.googleapis.com/" \
        f"v1alpha/{parent}/logs:import"
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
         },
      ],
      "forwarder": f"projects/{args.project_id}/"
                   f"locations/{args.region}/"
                   f"instances/{args.project_instance}/"
                   f"forwarders/{args.forwarder_id}"
    }
  }
  response = http_session.request("POST", url, json=body)
  if response.status_code >= 400:
    logging.error(f"Error response: {response.text}")
  response.raise_for_status()
  logging.info(f"Request successful with status code: {response.status_code}")
  return response.json()


if __name__ == "__main__":
  # Configure logging
  logging.basicConfig(
      level=logging.INFO,
      format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  )
  logger = logging.getLogger(__name__)

  parser = argparse.ArgumentParser()
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
    result = logs_import(auth_session, args.logs_file)
    logging.info("Import operation completed successfully")
    print(json.dumps(result, indent=2))
  except Exception as e:
    logging.error(f"Import operation failed: {str(e)}")
