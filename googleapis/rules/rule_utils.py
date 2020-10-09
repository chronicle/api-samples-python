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
"""Utility functions for use in the rule_lib module.

Chronicle customers should treat these functions as black boxes.
The function definitions and behaviors will not change, so the customer
should not be impacted if the implementation details change.
"""

import json


def parse_stream(response):
  """Parse stream response.

  The requests library provides utilities for iterating over the HTTP stream
  response, so we do not have to worry about chunked transfer encoding. The
  response is a stream of bytes that represent a json array.
  Each top-level element of the json array is a batch. The array is "never
  ending"; the server can send a batch at any time, thus
  adding to the json array.

  Args:
    response: The requests.Response Object returned from requests.post().

  Yields:
    Dictionary representations of each notification batch that was sent over the
    stream.
  """
  try:
    if response.encoding is None:
      response.encoding = "utf-8"

    for line in response.iter_lines(decode_unicode=True, delimiter="\r\n"):
      if not line:
        continue

      # Trim all characters before first opening brace, and after last closing
      # brace. Example:
      #   Input:  "  {'key1': 'value1'},  "
      #   Output: "{'key1': 'value1'}"
      json_string = "{" + line.split("{", 1)[1].rsplit("}", 1)[0] + "}"

      yield json.loads(json_string)

  except Exception as e:
    # Chronicle's servers will generally send a {"error": ...} dict over the
    # stream to indicate retryable failures (e.g. due to periodic internal
    # server maintenance), which will not cause this except block to fire.
    #
    # In rarer cases, the streaming connection may silently fail; the
    # connection will close without an error dict, which manifests as a
    # requests.exceptions.ChunkedEncodingError; see
    # https://github.com/urllib3/urllib3/issues/1516 for details from the
    # `requests` and `urllib3` community.
    #
    # Instead of allowing streaming clients to crash (for ChunkedEncodingErrors,
    # and for other Exceptions that may occur while reading from the stream),
    # we will catch exceptions, then yield a dict containing the error,
    # so the client may report the error, then retry connection (with backoff,
    # and retry limit).
    yield {
        "error": {
            "code": 500,
            "status": "UNAVAILBLE",
            "message": "exception caught while reading stream response (your "
                       "streaming client should retry connection): {}".format(
                           repr(e)),
        }
    }
