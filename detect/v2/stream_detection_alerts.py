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
"""Executable and reusable sample for streaming detection alerts.

API reference:
https://cloud.google.com/chronicle/docs/reference/detection-engine-api#streamdetectionalerts
"""

import argparse
import collections
import datetime
import json
import logging
import time
from typing import Any, Callable, Iterator, Mapping, Optional, Sequence, Tuple

from google.auth.transport import requests

from common import chronicle_auth
from common import datetime_converter
from common import regions

# Set up logger that will include timestamps.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s:%(levelname)s:%(name)s:%(message)s")
_LOGGER_ = logging.getLogger("stream_detection_alerts")

# Type alias for a detection batch, which comes from one stream response.
# A DetectionBatch is a tuple of (list of detections, continuation time).
DetectionBatch = Tuple[Sequence[Mapping[str, Any]], str]

# WEBHOOK_URL is used for chat ops integrations. The example shown below
# features slack webhooks, but will also work with google chat webhooks.
# The slack integration is disabled when WEBHOOK_URL is None.
# To try the slack webhook integration, populate WEBHOOK_URL with a string, e.g.
# WEBHOOK_URL = "https://hooks.slack.com/services/yourWebhookHere"
WEBHOOK_URL = None

# The following applies to the slack integration callback function.
# One detection batch might have lots of detections. We want to avoid
# dumping lots of UDM text into the terminal output or the slack chat room.
# For all detection batches, we'll summarize the detection batch (e.g. how
# many detections came from which rules).
# However, for detection batches with more detections than
# MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL,
# we'll omit reporting on each detection individually.
# Increase this if you're fine with noisier outputs.
MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL = 100

# The following applies to the slack integration callback function.
# See https://api.slack.com/changelog/2018-04-truncating-really-long-messages
# Long messages will be truncated after 40k characters (resulting in data being
# omitted). Additionally, long messages will be split into multiple messages,
# which will interrupt formatting blocks such as triple backticks, ```.
# To avoid both of the above, we can send multiple smaller messages.
# Each message posted will contain at most this many detections.
DETECTIONS_PER_WEBHOOK_MESSAGE = 3

CHRONICLE_API_BASE_URL = "https://backstory.googleapis.com"


def parse_stream(
    response: requests.requests.Response) -> Iterator[Mapping[str, Any]]:
  """Parses a stream response containing one detection batch.

  The requests library provides utilities for iterating over the HTTP stream
  response, so we do not have to worry about chunked transfer encoding. The
  response is a stream of bytes that represent a JSON array.
  Each top-level element of the JSON array is a detection batch. The array is
  "never ending"; the server can send a batch at any time, thus
  adding to the JSON array.

  Args:
    response: The response object returned from post().

  Yields:
    Dictionary representations of each detection batch that was sent over the
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
    # so the client may report the error, then retry connection (with backoff,
    # and retry limit).
    yield {
        "error": {
            "code": 503,
            "status": "UNAVAILBLE",
            "message": "exception caught while reading stream response. This "
                       "python client is catching all errors and is returning "
                       "error code 503 as a catch-all. The original error "
                       "message is as follows: {}".format(
                           repr(e)),
        }
    }


def callback_print(detection_batch: DetectionBatch):
  """Prints an abbreviated dump of a detection batch.

  Args:
    detection_batch: The detection batch to print.
  """
  detection_dump = json.dumps(detection_batch[0], indent=2)
  lines = 100
  detection_dump_abbr = "\n".join(detection_dump.split("\n")[:lines])
  print(
      f"First {lines} lines of the detection batch dump:\n{detection_dump_abbr}"
  )


def callback_slack_webhook(detection_batch: DetectionBatch):
  """Formats a detection batch, and sends it to a slack webhook.

  Args:
    detection_batch: The detection batch to send to slack.
  """

  if not WEBHOOK_URL:
    _LOGGER_.warning(
        "WEBHOOK_URL is not populated, skipping slack webhook integration")
    return

  detections = detection_batch[0]
  continuation_time = detection_batch[1]
  batch_size = len(detections)

  if not detections:
    return

  report_lines = []
  report_lines.append(
      f"Got stream response with continuationTime {continuation_time}," +
      f" containing {batch_size} detections.")

  # Aggregate by each rule version, and list the count of
  # associated detections. Recall that the server's detections
  # ARE NOT AGGREGATED, and are NOT SORTED in any particular grouping/order.
  # This aggregation is done entirely within this python client code.
  report_lines.append("Summary of detections:")
  # detection_metadatas is a list of the metadata (i.e., rule name, rule ID, and
  # version ID) from all the detections.
  detection_metadatas = []
  for detection in detections:
    # detection["detection"] is always a list that has one element.
    meta = detection["detection"][0]
    # ruleVersion is only populated for RULE_DETECTION type detections.
    rule_info = tuple((meta["ruleName"], meta["ruleId"], meta["ruleVersion"]
                      )) if detection["type"] == "RULE_DETECTION" else tuple(
                          (meta["ruleName"], meta["ruleId"]))
    detection_metadatas.append(rule_info)

  for detection_metadata, count in collections.Counter(
      detection_metadatas).items():
    line = f"\t{count} detections from Rule `{detection_metadata[0]}`" + f" (Rule ID `{detection_metadata[1]}`,"
    if len(detection_metadata) >= 3:
      line = line + f" Version ID `{detection_metadata[2]}`)"
    report_lines.append(line)

  if batch_size > MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL:
    # Avoid flooding our output channels.
    report_lines.append(
        "Omitting detections because more than" +
        f" {MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL} total detections" +
        " were received.")
    report_lines.append("")
    report_string = "\n".join(report_lines)
    requests.requests.post(WEBHOOK_URL, json={"text": report_string})
  else:
    # Output each detections's metadata and its UDM event samples.
    report_lines.append("Detections listed below:")
    for idx, detection in enumerate(detections):
      report_lines.append(f"{idx})")

      # This for loop includes rule name, rule ID, rule type, rule version,
      # rule set and other fields.
      for meta_key, meta_value in detection["detection"][0].items():
        report_lines.append(f"\t{meta_key}: {meta_value}")
      report_lines.append(f"\tTime Window: {detection['timeWindow']}")

      # The event samples list can be long. Report only one event
      # sample to avoid noisy output, and to avoid hitting slack's truncation.
      event_sample_dump = json.dumps(
          detection.get("collectionElements", [{}])[0].get("references",
                                                           [])[0:1],
          indent="\t")
      report_lines.append("One single event sample listed below:")
      report_lines.append(f"```{event_sample_dump}```")

      if idx % DETECTIONS_PER_WEBHOOK_MESSAGE == 0 or idx == batch_size - 1:
        # Construct a report string, then clear out report_lines so the
        # next iterations can start building an new list.
        report_string = "\n".join(report_lines)
        report_lines.clear()
        report_lines.append("")

        requests.requests.post(WEBHOOK_URL, json={"text": report_string})


def callback(detection_batch: DetectionBatch):
  """Single callback function that invokes callback helpers.

  Args:
    detection_batch: The detection batch to pass to the callback helpers.
  """
  callback_print(detection_batch)
  callback_slack_webhook(detection_batch)


def stream_detection_alerts(
    http_session: requests.AuthorizedSession,
    req_data: Mapping[str, Any],
    process_detection_batch_callback: Callable[[DetectionBatch], None],
) -> Tuple[int, str, str]:
  """Makes one call to stream_detection_alerts, and runs until disconnection.

  Each call to stream_detection_alerts streams all detection alerts found after
  req_data["continuationTime"].

  Initial connections should omit continuationTime from the connection request;
  in this case, the server will default the continuation time to the time of
  the connection.

  The server sends a stream of bytes, which is interpreted as a list of python
  dictionaries; each dictionary represents one "detection batch."

      - A detection batch might have the key "error";
        if it does, you should retry connecting with exponential backoff, which
        this function implements.
      - A detection batch might have the key "heartbeat";
        if it does, this is a "heartbeat detection batch", meant as a
        keep-alive message from the server, which your client can ignore.
      - If none of the above apply:
         - The detection batch is a "non-heartbeat detection batch".
           It will have a key, "continuationTime." This
           continuation time should be provided when reconnecting to
           stream_detection_alerts to continue receiving alerts from where the
           last connection left off; the most recent continuation time (which
           will be the maximum continuation time so far) should be provided.
         - The detection batch may optionally have a key, "detections",
           containing detection alerts from Rules Engine. The key will be
           omitted if no new detection alerts were found.

  Example heartbeat detection batch:
    {
      "heartbeat": true,
    }

  Example detection batch without detections list:
    {
      "continuationTime": "2019-08-01T21:59:17.081331Z"
    }

  Example detection batch with detections list:
    {
      "continuationTime": "2019-05-29T05:00:04.123073Z",
      "detections": [
         {contents of detection 1},
         {contents of detection 2}
      ]
    }

  The contents of a detection follow this format:
    {
      "id": "de_<UUID>",
      "type": "RULE_DETECTION"/"GCTI_FINDING",
      "createdTime": "yyyy-mm-ddThh:mm:ssZ",
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
      "detection": [  <-- this is always a list that has one element.
        {
          "ruleId": "ru_<UUID>"/"ur_ruleID",
          "ruleName": "<rule_name>",
          // ruleVersion is only populated for RULE_DETECTION type detections.
          "ruleVersion": "ru_<UUID>@v_<seconds>_<nanoseconds>",
          "urlBackToProduct": "<URL>",
          "alertState": "ALERTING"/"NOT_ALERTING",
          "ruleType": "SINGLE_EVENT"/"MULTI_EVENT",
          "detectionFields": [
            {
              "key": "<field name>",
              "value": "<field value>"
            }
          ],
          // Following fields are only populated for "GCTI_FINDING" type
          // detections.
          "summary": "Rule Detection",
          "ruleSet": "<rule set ID>",
          "ruleSetDisplayName": "<rule set display name>",
          "description": "<rule description>",
          "severity": "INFORMATIONAL"/"LOW"/"HIGH"
        },
      ],
      // Following fields are only populated for "GCTI_FINDING" type
      // detections.
      "lastUpdatedTime": "yyyy-mm-ddThh:mm:ssZ",
      "tags": ["<tag1>", "<tag2>", ...]
    }

  Args:
    http_session: Authorized session for HTTP requests.
    req_data: Dictionary containing connection request parameters (either empty,
      or contains they key, "continuationTime").
    process_detection_batch_callback: A callback functions that operates on a
      single detection batch. (e.g. to integrate with other platforms)

  Returns:
    Tuple containing (HTTP response status code from connection attempt,
    disconnection reason, continuation time string received in most recent
    non-heartbeat detection batch or empty string if no such non-heartbeat
    detection batch was received).
  """
  url = f"{CHRONICLE_API_BASE_URL}/v2/detect/rules:streamDetectionAlerts"

  response_code = 0
  disconnection_reason = ""
  continuation_time = ""

  # Heartbeats are sent by the server, approximately every 15s. Even if
  # no new detections are being produced, the server sends empty
  # batches.
  # We impose a client-side timeout of 300s (5 mins) between messages from the
  # server. We expect the server to send messages much more frequently due
  # to the heratbeats though; this timeout should never be hit, and serves
  # as a safety measure.
  # If no messages are received after this timeout, the client cancels
  # connection (then retries).
  with http_session.post(
      url, stream=True, data=req_data, timeout=300) as response:
    # Expected server response is a continuous stream of
    # bytes that represent a never-ending JSON array. The parsing
    # is handed by parse_stream. See docstring above for
    # formats of detections and detection batches.
    #
    # Example stream of bytes:
    # [
    #   {detection batch 1},
    #   # Some delay before server sends next batch...
    #   {detection batch 2},
    #   # Some delay before server sends next batch(es)...
    #   # The ']' never arrives, because we hold the connection
    #   # open until the connection breaks.
    _LOGGER_.info(
        "Initiated connection to detection alerts stream with request: %s",
        req_data)
    response_code = response.status_code
    if response.status_code != 200:
      disconnection_reason = (
          "connection refused with " +
          f"status={response.status_code}, error={response.text}")
    else:
      # Loop over each detection batch that is streamed. The following
      # loop will block, and an iteration only runs when the server
      # sends a detection batch.
      for batch in parse_stream(response):
        if "error" in batch:
          error_dump = json.dumps(batch["error"], indent="\t")
          disconnection_reason = f"connection closed with error: {error_dump}"
          break

        if "heartbeat" in batch:
          _LOGGER_.info("Got empty heartbeat (confirms connection/keepalive)")
          continue

        # When we reach this line, we have successfully received
        # a non-heartbeat detection batch.
        continuation_time = batch["continuationTime"]
        if "detections" not in batch:
          _LOGGER_.info("Got a new continuationTime=%s, no detections",
                        continuation_time)
          continue
        else:
          _LOGGER_.info("Got detection batch with continuationTime=%s",
                        continuation_time)

        # Process the batch using the callback.
        detections = batch["detections"]
        process_detection_batch_callback((detections, continuation_time))

  return (response_code, disconnection_reason, continuation_time)


def stream_detection_alerts_in_retry_loop(
    credentials_file: str,
    process_detection_batch_callback: Callable[[DetectionBatch], None],
    initial_continuation_time: Optional[datetime.datetime] = None,
):
  """Calls stream_detection_alerts and manages state for reconnections.

  Args:
    credentials_file: Path to credentials file, used to make an authorized
      session for HTTP requests.
    process_detection_batch_callback: A callback functions that operates on a
      single detection batch. (e.g. to integrate with other platforms)
    initial_continuation_time: A continuation time to be used in the initial
      stream_detection_alerts connection (default = server will set this to the
      time of connection). Subsequent stream_detection_alerts connections will
      use continuation times from past connections.

  Raises:
    RuntimeError: Hit retry limit after multiple consecutive failures
      without success.

  """
  continuation_time = datetime_converter.strftime(initial_continuation_time)

  # Our retry loop uses exponential backoff with a retry limit.
  # For simplicity, we retry for all types of errors.
  max_consecutive_failures = 7
  consecutive_failures = 0
  while True:
    if consecutive_failures > max_consecutive_failures:
      raise RuntimeError("exiting retry loop. consecutively failed " +
                         f"{consecutive_failures} times without success")

    if consecutive_failures:
      sleep_duration = 2**consecutive_failures
      _LOGGER_.info("sleeping %d seconds before retrying", sleep_duration)
      time.sleep(sleep_duration)

    req_data = {} if not continuation_time else {
        "continuationTime": continuation_time
    }

    # Connections may last hours. Make a new authorized session every retry loop
    # to avoid session expiration.
    session = chronicle_auth.initialize_http_session(credentials_file)

    # This function runs until disconnection.
    response_code, disconnection_reason, most_recent_continuation_time = stream_detection_alerts(
        session, req_data, process_detection_batch_callback)

    if most_recent_continuation_time:
      consecutive_failures = 0
      continuation_time = most_recent_continuation_time
    else:
      _LOGGER_.info(disconnection_reason
                    if disconnection_reason
                    else "connection unexpectedly closed")

      # Do not retry if the disconnection was due to invalid arguments.
      # We assume a disconnection was due to invalid arguments if the connection
      # was refused with HTTP status code 400.
      if response_code == 400:
        raise RuntimeError("exiting retry loop. connection refused " +
                           f"due to invalid arguments {req_data}")

      consecutive_failures += 1
      # Do not update continuation_time because the connection immediately
      # failed without receiving any non-heartbeat detection batches.
      # Retry with the same connection request as before.


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "-ct",
      "--continuation_time",
      type=datetime_converter.iso8601_datetime_utc,
      required=False,
      help="A timestamp for the initial stream_detection_alerts connection," +
      " in UTC ('yyyy-mm-ddThh:mm:ssZ')",
  )

  args = parser.parse_args()
  CHRONICLE_API_BASE_URL = regions.url(CHRONICLE_API_BASE_URL, args.region)
  stream_detection_alerts_in_retry_loop(
      args.credentials_file,
      callback,
      args.continuation_time,
  )
