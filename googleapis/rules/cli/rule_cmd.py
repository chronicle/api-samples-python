#!/usr/bin/env python3
# Copyright 2020 Google Inc.
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
"""Example python script accessing backstory's Rules API.
"""

import argparse
import logging
import os
import pprint
import sys

# We put the library for the rules API in the directory above this one. Make
# that directory part of the search path for imports. This looks a bit funky
# but it is the best way to get the path of the parent directory of this file's
# directory.
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

import rule_lib

_LOGGER_ = logging.getLogger(__name__)


ALLOWED_RPCS = [
    'GetRule',
    'ListRules',
    'CreateRule',
    'UpdateRule',
    'DeleteRule',
    'RunRule',
    'EnableLiveRule',
    'ListResults',
    'GetOperation',
    'ListOperations',
    'WaitOperation',
    'DeleteOperation',
    'CancelOperation',
]


def main():
  # Get the args passed into the function
  parser, args = _parse_args()

  # If verbose was setup, update the logging level early
  if args.verbose:
    logging.basicConfig(level=logging.INFO)

  # Create an instance of the rule api wrapper
  rule_wrap = rule_lib.RuleLib()

  res = ''
  rpc = args.rpc

  if rpc == 'GetRule':
    res = rule_wrap.get_rule(args.rule_id)
  elif rpc == 'ListRules':
    res = rule_wrap.list_rules()
  elif rpc == 'CreateRule':
    res = rule_wrap.create_rule_path(args.rule_path)
  elif rpc == 'UpdateRule':
    res = rule_wrap.update_rule_path(args.rule_id, args.rule_path)
  elif rpc == 'DeleteRule':
    res = rule_wrap.delete_rule(args.rule_id)
  elif rpc == 'RunRule':
    res = rule_wrap.run_rule(args.rule_id, args.start_time, args.end_time)
  elif rpc == 'EnableLiveRule':
    res = rule_wrap.enable_live_rule(args.rule_id)
  elif rpc == 'ListResults':
    res = rule_wrap.list_results(
        args.operation_id, args.page_size, args.page_token)
  elif rpc == 'GetOperation':
    res = rule_wrap.get_operation(args.operation_id)
  elif rpc == 'ListOperations':
    res = rule_wrap.list_operations()
  elif rpc == 'WaitOperation':
    res = rule_wrap.wait_operation(args.operation_id)
  elif rpc == 'DeleteOperation':
    res = rule_wrap.delete_operation(args.operation_id)
  elif rpc == 'CancelOperation':
    res = rule_wrap.cancel_operation(args.operation_id)
  else:
    parser.print_usage()
    sys.exit('rpc request was not recognized: %s' % rpc)

  if res:
    pprint.pprint(res)


def _parse_args():
  """Parse all command line args."""

  parser = argparse.ArgumentParser()
  parser.add_argument('rpc', type=str,
                      help='allowed commands: %s' % ALLOWED_RPCS)
  parser.add_argument('-rid', '--rule_id', type=str, default='',
                      help="rule id's start with ru_")
  parser.add_argument('-oid', '--operation_id', type=str, default='',
                      help="operation id's start with operations/rulejob_jo_")
  parser.add_argument('-rp', '--rule_path', type=str, default='',
                      help='path to a file containing a rule')
  parser.add_argument('-st', '--start_time', type=str, default='',
                      help='start time in RFC3339 format')
  parser.add_argument('-et', '--end_time', type=str, default='',
                      help='end time in RFC3339 format')
  parser.add_argument('-v', '--verbose', action='store_true', default=False,
                      help='make the logging output more verbose')
  parser.add_argument('-ps', '--page_size', type=int, default=0,
                      help='number of entries to return')
  parser.add_argument('-pt', '--page_token', type=str, default='',
                      help='page token to use to get next page')
  args = parser.parse_args()
  return (parser, args)


if __name__ == '__main__':
  main()
