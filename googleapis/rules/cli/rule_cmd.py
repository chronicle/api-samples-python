#!/usr/bin/env python3

# Copyright 2020 Google LLC
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
"""Example python script accessing the Chronicle Rules API."""

import argparse
import json
import logging
import os
import pprint
import sys

# We put the library for the rules API in the directory above this one. Make
# that directory part of the search path for imports. This looks a bit funky
# but it is the best way to get the path of the parent directory of this file's
# directory.
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))

import rule_lib

_LOGGER_ = logging.getLogger(__name__)

ALLOWED_RPCS = [
    "StreamRuleNotifications",
    "StreamDetections",
]


def main():
  # Get the args passed into the function.
  parser, args = _parse_args()

  # If verbose was setup, update the logging level early.
  if args.verbose:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")

  # Create an instance of the rule api wrapper.
  rule_wrap = rule_lib.RuleLib()

  res = ""
  rpc = args.rpc

  if rpc == "StreamRuleNotifications":
    res = rule_wrap.stream_rule_notifications(args.continuation_time)
  elif rpc == "StreamDetections":
    res = rule_wrap.stream_detections(args.continuation_time)

  else:
    parser.print_usage()
    sys.exit("rpc request was not recognized: %s" % rpc)

  if res:
    if args.output == "json":
      print(json.dumps(res))
    else:
      pprint.pprint(res)


def _parse_args():
  """Parse all command line args."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      "rpc", type=str, help="allowed commands: %s" % ALLOWED_RPCS)
  parser.add_argument(
      "-rid", "--rule_id", type=str, default="", help="rule IDs start with ru_")
  parser.add_argument(
      "-oid",
      "--operation_id",
      type=str,
      default="",
      help="operation IDs start with operations/rulejob_jo_")
  parser.add_argument(
      "-rp",
      "--rule_path",
      type=str,
      default="",
      help="path to a file containing a rule")
  parser.add_argument(
      "-st",
      "--start_time",
      type=str,
      default="",
      help="start time in RFC 3339 format")
  parser.add_argument(
      "-et",
      "--end_time",
      type=str,
      default="",
      help="end time in RFC 3339 format")
  parser.add_argument(
      "-v",
      "--verbose",
      action="store_true",
      default=False,
      help="make the logging output more verbose")
  parser.add_argument(
      "-ps",
      "--page_size",
      type=int,
      default=0,
      help="number of entries to return")
  parser.add_argument(
      "-pt",
      "--page_token",
      type=str,
      default="",
      help="page token to use to get next page")
  parser.add_argument(
      "-ct",
      "--continuation_time",
      type=str,
      default="",
      help="continuation time in RFC 3339 format, for notifications stream")
  parser.add_argument(
      "-o",
      "--output",
      type=str,
      default="python",
      help="output format. valid: json,python")
  args = parser.parse_args()
  return (parser, args)


if __name__ == "__main__":
  main()
