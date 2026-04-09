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
# pylint: disable=line-too-long
r"""Executable and reusable v1alpha API sample for finding raw logs in Chronicle.

API reference:
https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacyFindRawLogs
"""
# pylint: enable=line-too-long

import argparse
import json
from typing import List, Optional

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

DEFAULT_MAX_RESPONSE_SIZE = 52428800  # 50MiB in bytes


def find_raw_logs(http_session: requests.AuthorizedSession,
                  proj_id: str,
                  proj_instance: str,
                  proj_region: str,
                  query: str,
                  batch_tokens: Optional[List[str]] = None,
                  log_ids: Optional[List[str]] = None,
                  regex_search: bool = False,
                  case_sensitive: bool = False,
                  max_response_size: Optional[int] = None) -> None:
  # pylint: disable=line-too-long
  """Find raw logs in Chronicle using the Legacy Find Raw Logs API.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    query: Required search parameters that expand or restrict the search.
    batch_tokens: Optional list of tokens that should be downloaded.
    log_ids: Optional list of raw log ids that should be downloaded.
        If both batch_tokens and log_ids are provided, batch_tokens will be discarded.
    regex_search: Optional boolean to treat query as regex. Default is False.
    case_sensitive: Optional boolean for case-sensitive search. Default is False.
    max_response_size: Optional maximum response size in bytes. Default is 50MiB.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
        (response.status_code >= 400).

  Requires the following IAM permission on the instance resource:
  chronicle.legacies.legacyFindRawLogs
  """
  # pylint: enable=line-too-long
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL, proj_region)
  # pylint: disable-next=line-too-long
  instance = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{instance}/legacy:legacyFindRawLogs"

  # Build query parameters
  params = [f"query={query}"]
  if batch_tokens and not log_ids:  # log_ids take precedence over batch_tokens
    for token in batch_tokens:
      params.append(f"batchToken={token}")
  if log_ids:
    for log_id in log_ids:
      params.append(f"ids={log_id}")
  if regex_search:
    params.append("regexSearch=true")
  if case_sensitive:
    params.append("caseSensitive=true")
  if max_response_size:
    params.append(f"maxResponseByteSize={max_response_size}")

  url = f"{url}?{'&'.join(params)}"

  response = http_session.request("GET", url)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()

  result = response.json()
  print(json.dumps(result, indent=2))

  if result.get("too_many_results"):
    print("\nWarning: Some results were omitted due to too many matches.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  # common
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  # local
  parser.add_argument(
      "--query",
      type=str,
      required=True,
      help="Search parameters that expand or restrict the search")
  parser.add_argument(
      "--batch_tokens",
      type=str,
      help=
      'JSON string containing a list of batch tokens '
      ' (e.g., \'["token1", "token2"]\')'
  )
  parser.add_argument(
      "--log_ids",
      type=str,
      help=
      'JSON string containing a list of raw log IDs (e.g., \'["id1", "id2"]\')')
  parser.add_argument("--regex_search",
                      action="store_true",
                      help="Whether to treat the query as a regex pattern")
  parser.add_argument("--case_sensitive",
                      action="store_true",
                      help="Whether to perform a case-sensitive search")
  parser.add_argument(
      "--max_response_size",
      type=int,
      help=
      f"Maximum response size in bytes (default: {DEFAULT_MAX_RESPONSE_SIZE})")

  args = parser.parse_args()

  # Convert JSON strings to lists if provided
  batch_tokens_list = json.loads(
      args.batch_tokens) if args.batch_tokens else None
  log_ids_list = json.loads(args.log_ids) if args.log_ids else None

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  find_raw_logs(auth_session, args.project_id, args.project_instance,
                args.region, args.query, batch_tokens_list, log_ids_list,
                args.regex_search, args.case_sensitive, args.max_response_size)
