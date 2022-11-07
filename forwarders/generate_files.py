#!/usr/bin/env python3

# Copyright 2022 Google LLC
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
"""Executable and reusable sample for retrieving a list of feeds."""

import argparse
from typing import Mapping, Any

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def generate_files(http_session: requests.AuthorizedSession,
                   name: str) -> Mapping[str, Any]:
  """Retrieves all forwarders for the tenant.

  Args:
    http_session: Authorized session for HTTP requests.
    name: Unique name for the forwarder.

  Returns:
    Array containing each line of the forwarder's content.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/{name}:generateForwarderFiles"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "config": "<CONFIG FILE CONTENTS>",
  #   "auth": "<AUTH FILE CONTENTS>",
  # }

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-n",
      "--name",
      type=str,
      required=True,
      help="resource name for the Forwarder (forwarders/{UUID})")
  parser.add_argument(
      "-o",
      "--output",
      type=str,
      help="Writes configuration files to the specified output directory.")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  res = generate_files(session, args.name)

  output_dir = args.output
  if "config" in res:
    config = res["config"]
    if output_dir:
      with open(output_dir + "/forwarder.conf", "w") as f:
        f.write(config)
    else:
      print("forwarder.conf:\n", config)
  if "auth" in res:
    auth = res["auth"]
    if output_dir:
      with open(output_dir + "/forwarder_auth.conf", "w") as f:
        f.write(auth)
    else:
      print("forwarder_auth.conf:\n", auth)
