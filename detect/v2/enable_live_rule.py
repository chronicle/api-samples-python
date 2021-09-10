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
"""Executable and reusable sample for enabling a live detection rule.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#enableliverule
"""

import argparse

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def enable_live_rule(http_session: requests.AuthorizedSession, rule_id: str):
  """Enables a detection rule as live.

  The rule will run continuously against all *new* logs that your organization
  has that fall after the time the rule was enabled as live.

  To stop the rule from running, you can call the corresponding
  "disable_live_rule" action.

  If a version of a detection rule is enabled as live, then is updated with a
  new version, the following happens automatically:
  - The old version is disabled.
  - The new version is enabled as live.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_id: Unique ID of the detection rule to enable ("ru_<UUID>"). A version
      suffix should not be provided, because at most one version of a detection
      rule (by default the latest version of a rule) can be enabled at a time.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{rule_id}:enableLiveRule"
  response = http_session.request("POST", url)
  # Expected server response:
  # {}

  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-ri", "--rule_id", type=str, required=True, help="rule ID ('ru_<UUID>')")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  enable_live_rule(session, args.rule_id)
