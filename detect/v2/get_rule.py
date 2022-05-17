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
"""Executable and reusable sample for retrieving a detection rule.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#getrule
"""

import argparse
import json
from typing import Any, Mapping

from google.auth.transport import requests

from common import chronicle_auth
from common import regions

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def get_rule(http_session: requests.AuthorizedSession,
             version_id: str) -> Mapping[str, Any]:
  """Retrieves the content of a specific version of a specific detection rule.

  Args:
    http_session: Authorized session for HTTP requests.
    version_id: Unique ID of the detection rule to retrieve ("ru_<UUID>" or
      "ru_<UUID>@v_<seconds>_<nanoseconds>"). If a version suffix isn't
      specified we use the rule's latest version.

  Returns:
    Content and metadata about the requested detection rule, which is used to
    evaluate logs.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules/{version_id}"

  response = http_session.request("GET", url)
  # Expected server response:
  # {
  #   "ruleId": "ru_<UUID>",
  #   "versionId": "ru_<UUID>@v_<seconds>_<nanoseconds>",
  #   "ruleName": "<rule_name>",
  #   "metadata": {
  #     "<key_1>": "<value_1>",
  #     "<key_2>": "<value_2>",
  #     ...
  #   },
  #   "ruleText": "<rule_content>",
  #   "alertingEnabled": true, <-- IFF alerting is enabled.
  #   "liveRuleEnabled": true, <-- IFF a live rule is enabled.
  #   "versionCreateTime": "yyyy-mm-ddThh:mm:ss.ssssssZ",
  #   "compilationState": "SUCCEEDED"/"FAILED",
  #   "compilationError": "<error_message>", <-- IFF compilation failed.
  #   "archivedTime": "yyyy-mm-ddThh:mm:ss.ssssssZ", <-- IFF archived.
  #   "ruleType": "MULTI_EVENT"/"SINGLE_EVENT",
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
      "-vi",
      "--version_id",
      type=str,
      required=True,
      help="version ID ('ru_<UUID>[@v_<seconds>_<nanoseconds>]')")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  rule = get_rule(session, args.version_id)
  print(json.dumps(rule, indent=2))
