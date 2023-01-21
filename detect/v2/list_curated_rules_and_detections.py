#!/usr/bin/env python3

# Copyright 2023 Google LLC
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
"""Executable and reusable sample for listing curated rules followed by a sample of their detections.

This module demonstrates combining multiple single-purpose modules into a larger
workflow.
"""

import argparse
import json
import time
from typing import Any, List, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import regions
from . import list_curated_rule_detections
from . import list_curated_rules

_chronicle_api_base_url = "https://backstory.googleapis.com"

# Sleep duration to ensure we don't exceed QPM limit.
_DEFAULT_SLEEP_SECONDS = 6


def list_curated_rules_and_detections(
    http_session: requests.AuthorizedSession,
    page_size: int = 10,
    sleep_seconds: int = _DEFAULT_SLEEP_SECONDS
) -> List[Tuple[str, Sequence[Mapping[str, Any]], str]]:
  """Retrieves all curated rules with detections and the first page of up to page_size detections per curated rule.

  Args:
    http_session: Authorized session for HTTP requests.
    page_size: The maximum number of detections to retrieve for the first page
      of detections. Defaults to 10 if not specified.
    sleep_seconds: The maximum time to wait before making an additional call to
      ListCuratedRuleDetections. Defaults to 6 seconds if not specified.

  Returns:
    The curated rule ID, a maximum of page_size detections ordered by descending
    detection_time, and a Base64 token for getting the detections of the
    next page (an empty token string means the currently retrieved page is the
    last one) for each curated rule.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  # Keep retrieving curated rules until there are no more.
  page_token = ""
  all_curated_rules = []
  while True:
    curated_rules, page_token = list_curated_rules.list_curated_rules(
        http_session, page_token=page_token)
    all_curated_rules.append(curated_rules)
    if not page_token:
      break

  all_detections_and_tokens = []
  for page in all_curated_rules:
    for rule in page:
      rule_id = rule["ruleId"]
      first_page = list_curated_rule_detections.list_curated_rule_detections(
          http_session, rule_id, page_size=page_size)
      all_detections_and_tokens.append((rule_id, first_page[0], first_page[1]))
      print(
          f"Received {len(first_page[0])} detection(s) for rule {rule_id} with next_page_token {first_page[1]}"
      )
      time.sleep(sleep_seconds)

  return all_detections_and_tokens


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-s",
      "--page_size",
      type=int,
      required=False,
      help="maximum number of detections to return in the first page per curated rule"
  )

  args = parser.parse_args()
  _chronicle_api_base_url = regions.url(_chronicle_api_base_url, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  responses = list_curated_rules_and_detections(session, args.page_size)

  for response in responses:
    print("====================================")
    print(
        f"Displaying detections for the first page of detections for rule ID {response[0]}"
    )
    print(json.dumps(response[1], indent=2))
    print(f"Next page token: {response[2]}")
