#!/usr/bin/env python3

# Copyright 2024 Google LLC
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
r"""Executable and reusable sample for patching a Reference List.

Command supports add, remove, and replace via [--add, --remove, <no-flag>].

Sample Commands (run from api_samples_python dir):

# Add
python -m lists.v1alpha.patch_list \
 --project_id=$PROJECT_ID   \
 --project_instance=$PROJECT_INSTANCE \
 --name="COLDRIVER_SHA256" \
 --list_file=./lists/example_input/foo.txt \
 --add

# Remove
python -m lists.v1alpha.patch_list \
 --project_id=$PROJECT_ID   \
 --project_instance=$PROJECT_INSTANCE \
 --name="COLDRIVER_SHA256"
 --list_file=./lists/example_input/foo.txt \
 --remove

# Replace (when no --add or --remove flags are provided)
python -m lists.v1alpha.patch_list \
 --project_id=$PROJECT_ID   \
 --project_instance=$PROJECT_INSTANCE \
 --name="COLDRIVER_SHA256"
 --list_file=./lists/example_input/coldriver_sha256.txt

API reference:

 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists/patch
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#ReferenceList
 https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.referenceLists#resource:-referencelist
"""

import argparse
import json
import random
import sys
import time
from typing import Any, Dict, Optional, Sequence

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions
from google.auth.transport import requests

# pylint: disable=g-import-not-at-top
try:
  from . import get_list
except ImportError:
  from lists.v1alpha import get_list

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]
PREFIX = "REFERENCE_LIST_SYNTAX_TYPE_"
SYNTAX_TYPE_ENUM = [
    f"{PREFIX}UNSPECIFIED",  #	Defaults to ..._PLAIN_TEXT_STRING.
    f"{PREFIX}PLAIN_TEXT_STRING",  #	List contains plain text patterns.
    f"{PREFIX}REGEX",  #	List contains only Regular Expression patterns.
    f"{PREFIX}CIDR",  # List contains only CIDR patterns.
]


def patch_list(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    name: str,
    content_lines: Sequence[str],
    syntax_type: Optional[str] = None,
    description: Optional[str] = None,
    scope_name: Optional[str] = None,
) -> Dict[str, Any]:
  """Updates a Reference List.

  After update, the contents of the list are verified with Get List.
  If the contents are found to be different, updates are retried
   N times (configurable) with exponential backoff.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: region in which the target project is located.
    name: name that identifies the list to update.
    content_lines: Array containing each line of the list's content.
    syntax_type: (Optional) List content type; how to interpret this list.
    description: (Optional) Description of the list.
    scope_name: (Optional) Data RBAC scope name.
  Returns:
    Dictionary representation of the updated Reference List.

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      proj_region
  )

  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/referenceLists/{name}"
  body = {
      "entries": [{"value": line.strip()} for line in content_lines],
  }
  if scope_name:
    body["scope_info"] = {
        "referenceListScope": {
            "scopeNames": [
                f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}/dataAccessScopes/{scope_name}"
            ]
        }
    }
  else:
    body["scope_info"] = None  # does *not* remove scope_info
  if description:
    body["description"] = description
  if syntax_type:
    body["syntax_type"] = syntax_type

  params = {"updateMask": ",".join(body.keys())}
  body["name"] = name
  response = http_session.request("PATCH", url, params=params, json=body)
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


def parse_arguments():
  """Parses command line arguments."""
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter,
  )
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  parser.add_argument("-n", "--name", type=str, required=True,
                      help="unique name for the list")
  parser.add_argument("-f", "--list_file", type=argparse.FileType("r"),
                      required=True,
                      help="path of a file containing the list content")
  parser.add_argument("-d", "--description", type=str,
                      help="description of the list")
  parser.add_argument(
      "-s", "--scope_name", type=str, help="data RBAC scope name for the list"
  )
  parser.add_argument("-t", "--syntax_type", type=str, default=None,
                      choices=SYNTAX_TYPE_ENUM,
                      help="syntax type of the list, used for validation")
  add_delete_group = parser.add_mutually_exclusive_group()
  add_delete_group.add_argument("--add", action="store_true",
                                help="only append to the existing list")
  add_delete_group.add_argument("--remove", action="store_true",
                                help="only remove from the existing list")
  parser.add_argument("--force", action="store_true",
                      help="patch regardless of pre-check on changes to list")
  parser.add_argument("--max_attempts", type=int, default=6,
                      help="how many times to attempt the patch operation")
  parser.add_argument("--quiet", action="store_true",
                      help="only print the updated list")
  return parser.parse_args()


def read_content_lines(file_handle):
  """Reads content lines from a file into a list."""
  file_handle.seek(0)  # rewind in case this isn't 1st read
  return [line.strip() for line in file_handle]


def exponential_backoff(attempt, max_attempts, wait_time=1, quiet=False):
  """Exponential backoff for a given attempt."""
  if attempt > 0:
    jitter = random.uniform(0, wait_time / 2)
    wait_time = wait_time * 1.5
    time_to_sleep = wait_time + jitter
    if not quiet:
      print(f"Attempt {attempt} of {max_attempts} failed, "
            f"retrying in {time_to_sleep:.2f} seconds...")
    time.sleep(time_to_sleep)
  return wait_time


def get_current_state(auth_session, args):
  """Gets the current state of a Reference List."""
  curr_json = get_list.get_list(
      auth_session,
      args.project_id,
      args.project_instance,
      args.region,
      args.name,
  )
  curr_list = [_["value"] for _ in curr_json.get("entries", [])]
  return curr_list, curr_json["revisionCreateTime"]


def op_update_content_lines(operation_type, curr_list, content_lines,
                            force=False):
  """Updates the content lines of a Reference List."""
  if operation_type == "add":
    seen = set(curr_list)
    deduplicated_list = [x for x in content_lines
                         if not (x in seen or seen.add(x))]
    content_lines = curr_list + deduplicated_list
  elif operation_type == "remove":
    content_lines = [item for item in curr_list if item not in content_lines]
  if set(curr_list) == set(content_lines) and not force:
    print(f"Patch {operation_type or ''} would not change list. Exiting.")
    sys.exit(0)
  return content_lines


def main():
  args = parse_arguments()
  og_content_lines = read_content_lines(args.list_file)

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES
  )

  operation_type = "add" if args.add else "remove" if args.remove else None

  curr_list, _ = get_current_state(auth_session, args)

  content_lines = op_update_content_lines(
      operation_type, curr_list, og_content_lines, args.force)

  attempt, wait_time = 0, 1
  while attempt < args.max_attempts:
    patched_json = patch_list(
        auth_session,
        args.project_id,
        args.project_instance,
        args.region,
        args.name,
        content_lines,
        args.syntax_type,
        args.description,
        args.scope_name,
    )
    updated_list, ts = get_current_state(auth_session, args)
    # no need to compare sets if updated ts matches
    success = ts == patched_json["revisionCreateTime"]
    if not success:
      success = set(content_lines) == set(updated_list)

    if success:
      if not args.quiet:
        print(f"Patch {operation_type or ''} success.")
      print(json.dumps(patched_json, indent=2))
      break
    wait_time = exponential_backoff(attempt, args.max_attempts,
                                    wait_time, args.quiet)
    # read and verify again in case other processes updated while waiting
    og_content_lines = read_content_lines(args.list_file)
    curr_list, _ = get_current_state(auth_session, args)
    content_lines = op_update_content_lines(operation_type,
                                            curr_list,
                                            og_content_lines,
                                            args.force)
    attempt += 1


if __name__ == "__main__":
  main()
