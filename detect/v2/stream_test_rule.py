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
"""Executable and reusable sample for testing a rule without persisting results.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#streamtestrule
"""

import argparse
import datetime
import json
import logging
from typing import Any, Iterator, Mapping, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter
from common import regions

# Set up logger that will include timestamps.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
_LOGGER_ = logging.getLogger("stream_test_rule")

# Type alias for a result, which comes from one stream response.
# A Result is a either a detection or rule execution error.
Result = Mapping[str, Any]

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def parse_stream(
    response: requests.requests.Response) -> Iterator[Mapping[str, Any]]:
  """Parses a stream response containing one result.

  The requests library provides utilities for iterating over the HTTP stream
  response, so we do not have to worry about chunked transfer encoding. The
  response is a stream of bytes that represent a JSON array.
  Each top-level element of the JSON array is a result. The server can send a
  result at any time, thus adding to the JSON array. The array should end when
  the stream closes.

  Args:
    response: The response object returned from post().

  Yields:
    Dictionary representations of each result that was sent over the
    stream.
  """
  try:
    if response.encoding is None:
      response.encoding = "utf-8"

    for line in response.iter_lines(decode_unicode=True, delimiter="\r\n"):
      if not line:
        continue

      # Don't try to parse a line as JSON if it doesn't contain an opening and
      # closing brace.
      # This can happen when no JSON elements are streamed and the stream
      # closes, which is a normal case when testing a rule that doesn't generate
      # any results.
      if len(line.split("{", 1)) < 2 and len(line.rsplit("}", 1)) < 2:
        continue

      # Trim all characters before first opening brace, and after last closing
      # brace. Example:
      #   Input:  "  {'key1': 'value1'},  "
      #   Output: "{'key1': 'value1'}"
      json_string = "{" + line.split("{", 1)[1].rsplit("}", 1)[0] + "}"
      yield json.loads(json_string)

  except Exception as e:  # pylint: disable=broad-except
    # Chronicle's servers will generally send a {"error": ...} dict over the
    # stream to indicate retryable failures (e.g. due to periodic internal
    # server maintenance), which will not cause this except block to fire.
    #
    # In rarer cases, the streaming connection may silently fail; the
    # connection will close without an error dict, which manifests as a
    # requests.requests.exceptions.ChunkedEncodingError; see
    # https://github.com/urllib3/urllib3/issues/1516 for details from the
    # `requests` and `urllib3` community.
    #
    # Instead of allowing streaming clients to crash (for ChunkedEncodingErrors,
    # and for other Exceptions that may occur while reading from the stream),
    # we will catch exceptions, then yield a dict containing the error,
    # so the client may report the error.
    yield {
        "error": {
            "code": 503,
            "status": "UNAVAILABLE",
            "message": "exception caught while reading stream response. This "
                       "python client is catching all errors and is returning "
                       "error code 503 as a catch-all. The original error "
                       "message is as follows: {}".format(repr(e)),
        }
    }


def stream_test_rule(
    http_session: requests.AuthorizedSession,
    req_data: Mapping[str,
                      Any]) -> Tuple[Sequence[Result], Sequence[Result], str]:
  """Makes one call to stream_test_rule, and runs until disconnection.

  Each call to stream_test_rule streams all detections/rule execution errors
  found for the given rule and time range. The number of detections streamed
  is capped at the given number of max results. If a max number of results
  is not specified, a server-side default is used.

  The server sends a stream of bytes, which is interpreted as a list of python
  dictionaries; each dictionary represents one "result."

      - A result might have the key "error", either containing a rule execution
        error from Rules Engine or an error related to connection failure. If
        a connection failure error is returned, a RuntimeError will be
        raised indicating that you should retry testing the rule.
      - A result might have the key "detection", containing a detection from
        Rules Engine.

  The contents of a detection follow this format:
    {
      "id": "de_<UUID>",
      "type": "RULE_DETECTION",
      "detectionTime": "yyyy-mm-ddThh:mm:ssZ",
      "timeWindow": {
        "startTime": "yyyy-mm-ddThh:mm:ssZ",
        "endTime": "yyyy-mm-ddThh:mm:ssZ",
      }
      "collectionElements": [
        {
          "label": "e1",
          "references": [
            {
              "event": <UDM keys and values / sub-dictionaries>...
            },
            ...
          ],
        },
        {
          "label": "e2",
          ...
        },
        ...
      ],
      "detection": [
        {
          "ruleName": "<rule_name>",
          "ruleType": "SINGLE_EVENT"/"MULTI_EVENT",
          "detectionFields": [
            {
              "key": "<field name>",
              "value": "<field value>"
            }
          ]
        },
      ],
    }

  The contents of a rule execution error follow this format:
    {
      "category": "RULES_EXECUTION_ERROR",
      "text": <error message>,
      "ruleExecution": {
        windowStartTime: "yyyy-mm-ddThh:mm:ssZ",
        windowEndTime: "yyyy-mm-ddThh:mm:ssZ",
      },
    }

  Args:
    http_session: Authorized session for HTTP requests.
    req_data: Dictionary containing connection request parameters
      (contains keys "rule.rule_text", "start_time", "end_time", and
      optionally "max_results".)

  Returns:
    Tuple containing (all detections successfully streamed back, all rule
    execution errors successfully streamed back, disconnection reason)
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules:streamTestRule"

  detections = []
  execution_errors = []
  disconnection_reason = ""

  # Results should be streamed continuously.
  # We impose a client-side timeout of 180s (3 mins) between streamed results.
  # This should be enough time to handle delays in streaming back
  # the first result.
  with http_session.post(
      url, stream=True, data=req_data, timeout=180) as response:
    # Expected server response is a continuous stream of
    # bytes that represent a JSON array. The parsing
    # is handed by parse_stream. See docstring above for
    # formats of detections and rule execution errors.
    #
    # Example stream of bytes:
    # [
    #   {detection 1},
    #   # Some delay before server sends next result...
    #   {rule execution error 1},
    #   # Some delay before server sends next result(s)...
    #   # We expect the ']' to arrive if all results are streamed before a
    #   # server-side timeout; otherwise, a connection failure error may be
    #   # streamed back if/when the connection breaks.
    _LOGGER_.info("Initiated connection to test rule stream")
    if response.status_code >= 400:
      disconnection_reason = (
          "connection closed with " +
          f"status={response.status_code}, error={response.text}")
    else:
      for result in parse_stream(response):
        res = None
        if "detection" in result:
          _LOGGER_.info("Got detection")
          res = result["detection"]
          detections.append(res)
        elif "error" in result:
          # We distinguish rule execution errors from
          # other errors sent back over the stream by checking to see if
          # the error has the RULES_EXECUTION_ERROR category.
          error = result["error"]
          if error.get("category") == "RULES_EXECUTION_ERROR":
            _LOGGER_.info("Got rule execution error")
            res = error
            execution_errors.append(res)
          else:
            error_dump = json.dumps(error, indent="\t")
            disconnection_reason = f"connection aborted with error={error_dump}"
            break

        # Print an abbreviated dump of a result if it was successfully received.
        if res:
          result_dump = json.dumps(res, indent=2)
          lines = 100
          result_dump_abbr = "\n".join(result_dump.split("\n")[:lines])
          print(f"First {lines} lines of the result dump:\n{result_dump_abbr}")

  return (detections, execution_errors, disconnection_reason)


def test_rule(http_session: requests.AuthorizedSession,
              rule_content: str,
              event_start_time: datetime.datetime,
              event_end_time: datetime.datetime,
              max_results: int = 0):
  """Calls stream_test_rule once to test rule.

  Args:
    http_session: Authorized session for HTTP requests.
    rule_content: Content of a detection rule, used to evaluate logs.
    event_start_time: Start time of the time range of logs to test rule over.
    event_end_time: End time of the time range of logs to test rule over
      (max allowed time range duration is 2 weeks).
    max_results: Maximum number of detections to return.
      Must be nonnegative and is capped at a server-side limit of 10,000.
      Optional - if not specified, a server-side default of 1,000 is used.

  Raises:
    RuntimeError: Streaming connection was unexpectedly closed or aborted.
  """
  req_data = {
      "rule.rule_text": rule_content,
      "start_time": datetime_converter.strftime(event_start_time),
      "end_time": datetime_converter.strftime(event_end_time),
      "max_results": max_results
  }

  dets, errs, disconnection_reason = stream_test_rule(http_session, req_data)

  # Print out the total number of detections/rule execution errors
  # that were successfully found from testing the rule, up to the point
  # of disconnection.
  print(f"Got {len(dets)} detections and {len(errs)} rule execution errors")

  if disconnection_reason:
    raise RuntimeError(f"Connection failed: {disconnection_reason}. Retry "
                       "testing the rule.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-f",
      "--rule_file",
      type=argparse.FileType("r"),
      required=True,
      # File example: python3 stream_test_rule.py -f <path>
      # STDIN example: cat rule.txt | python3 stream_test_rule.py -f -
      help="path of a file with the desired rule's content, or - for STDIN")
  parser.add_argument(
      "-st",
      "--event_start_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="event start time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-et",
      "--event_end_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=True,
      help="event end time in UTC ('yyyy-mm-ddThh:mm:ssZ')")
  parser.add_argument(
      "-mr",
      "--max_results",
      type=int,
      required=False,
      help="maximum number of detections to stream back")

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  session = chronicle_auth.initialize_http_session(args.credentials_file)
  test_rule(session, args.rule_file.read(), args.event_start_time,
            args.event_end_time, args.max_results)
