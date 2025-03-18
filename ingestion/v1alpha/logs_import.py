#!/usr/bin/env python3

import argparse
import base64
import json

from google.auth.transport import requests

from common import chronicle_auth
from common import project_instance
from common import project_id
from common import regions

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

#LOGS = base64.b64encode(b"""2024-01-29 09:03:06.000000001 client 192.168.109.254#12345: query: google.com IN A + (1.2.3.4)
#2024-01-29 09:03:07.000000001 client 192.168.109.252#12345: query: bbc.com IN A + (5.6.7.8)
#""").decode("utf-8")

def logs_import(http_session: requests.AuthorizedSession, logs_file) -> None:
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
  body = {
    "inline_source": {
      "logs": [
        {
          "data": logs,
          "log_entry_time": "2025-01-29T15:01:23.045123456Z",
          "collection_time": "2025-01-29T16:01:23.045123456Z",
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
    print(response.text)
  response.raise_for_status()
  print(response.status_code)
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
  print(json.dumps(logs_import(auth_session, args.logs_file)))
