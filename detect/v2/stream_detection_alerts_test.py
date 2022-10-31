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
"""Unit tests for the "stream_detection_alerts" module."""

import json
import unittest
from unittest import mock

from google.auth.transport import requests

from common import chronicle_auth
from . import stream_detection_alerts


class StreamDetectionAlertsTest(unittest.TestCase):

  @mock.patch("time.sleep", return_value=None)
  @mock.patch.object(chronicle_auth, "initialize_http_session", autospec=True)
  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_http_error(self, mock_session, mock_init_session, mock_sleep):
    mock_init_session.return_value = mock_session
    # Mock a streaming connection failure with a non-400 status code.
    mock_session.post.return_value.__enter__.return_value.status_code = 429

    # Prepare string representations of detection batches that can
    # passed to callback functions.
    mock_detection_batches = [
        tuple(([], "2020-12-08T22:39:55.633014925Z")),
    ]
    detection_batch_dumps = []
    for batch in mock_detection_batches:
      detection_batch_dumps.append(
          f'{{"continuationTime": "{batch[1]}",' +
          f' "detections": {json.dumps(batch[0])}}}')

    # Make the streamed responses from response.iter_lines() return our
    # detection batches.
    mock_session.post.return_value.__enter__.return_value.iter_lines.side_effect = [
        detection_batch_dumps,
    ]

    # Track how many times the callback functions get called.
    callback_count = 0

    def mock_callback(_):
      nonlocal callback_count
      callback_count += 1

    # Call stream_detection_alerts, using our mock callback.
    # RuntimeError occurs when retry loop hits its limit.
    with self.assertRaises(RuntimeError):
      stream_detection_alerts.stream_detection_alerts_in_retry_loop(
          "credentials_file", mock_callback)

    # The callback function should never get called, because the
    # mocked connection always fails in this test case.
    self.assertEqual(0, callback_count)

    # Session should have been initialized more times than
    # the polling loop slept, since the last iteration exits early.
    self.assertGreater(mock_init_session.call_count, mock_sleep.call_count)

    # The retry loop should have ran more than once before exiting.
    self.assertGreater(mock_sleep.call_count, 1)

  @mock.patch("time.sleep", return_value=None)
  @mock.patch.object(chronicle_auth, "initialize_http_session", autospec=True)
  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_invalidargs_http_error(self, mock_session, mock_init_session,
                                  mock_sleep):
    mock_init_session.return_value = mock_session
    # Mock a streaming connection failure with a 400 status code.
    # This indicates that invalid arguments were passed to the sample.
    mock_session.post.return_value.__enter__.return_value.status_code = 400

    # Prepare string representations of detection batches that can
    # passed to callback functions.
    mock_detection_batches = [
        tuple(([], "2020-12-08T22:39:55.633014925Z")),
    ]
    detection_batch_dumps = []
    for batch in mock_detection_batches:
      detection_batch_dumps.append(
          f'{{"continuationTime": "{batch[1]}",' +
          f' "detections": {json.dumps(batch[0])}}}')

    # Make the streamed responses from response.iter_lines() return our
    # detection batches.
    mock_session.post.return_value.__enter__.return_value.iter_lines.side_effect = [
        detection_batch_dumps,
    ]

    # Track how many times the callback functions get called.
    callback_count = 0

    def mock_callback(_):
      nonlocal callback_count
      callback_count += 1

    # Call stream_detection_alerts, using our mock callback.
    # RuntimeError occurs when connection immediately fails with 400 status
    # code.
    with self.assertRaises(RuntimeError):
      stream_detection_alerts.stream_detection_alerts_in_retry_loop(
          "credentials_file", mock_callback)

    # The callback function should never get called, because the
    # mocked connection always fails in this test case.
    self.assertEqual(0, callback_count)

    # Session should have been initialized exactly once,
    # since the retry loop only should have ran once before exiting.
    self.assertEqual(mock_init_session.call_count, 1)

    # No sleeps should have occurred, since no retries should have
    # occurred.
    self.assertEqual(mock_sleep.call_count, 0)

  @mock.patch("time.sleep", return_value=None)
  @mock.patch.object(chronicle_auth, "initialize_http_session", autospec=True)
  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def tests_happy_path(self, mock_session, mock_init_session, mock_sleep):
    mock_init_session.return_value = mock_session
    # Mock a successful streaming connection.
    mock_session.post.return_value.__enter__.return_value.status_code = 200

    mock_detection_template = {
        "id":
            "PLACEHOLDER",  # To be replaced with unique ID.
        "type":
            "RULE_DETECTION",
        "createdTime":
            "2020-11-05T12:00:00Z",
        "detectionTime":
            "2020-11-05T01:00:00Z",
        "timeWindow": {
            "startTime": "2020-11-05T00:00:00Z",
            "endTime": "2020-11-05T01:00:00Z",
        },
        "detection": [{
            "ruleId":
                "ru_12345678-1234-1234-1234-1234567890ab",
            "ruleName":
                "rule content",
            "ruleVersion":
                "ru_12345678-1234-1234-1234-1234567890ab@v_100000_000000",
            "urlBackToProduct":
                "https://chronicle.security",
            "alertState":
                "ALERTING",
            "ruleType":
                "MULTI_EVENT",
            "detectionFields": [{
                "key": "fieldName",
                "value": "fieldValue",
            }]
        }],
    }

    mock_uppercase_detection_template = {
        "id":
            "PLACEHOLDER",  # To be replaced with unique ID.
        "type":
            "GCTI_FINDING",
        "createdTime":
            "2020-11-05T12:00:00Z",
        "detectionTime":
            "2020-11-05T01:00:00Z",
        "timeWindow": {
            "startTime": "2020-11-05T00:00:00Z",
            "endTime": "2020-11-05T01:00:00Z",
        },
        "lastUpdatedTime": "2020-11-05T12:00:00Z",
        "tags": ["TA0005", "TA0003", "T1098.004"],
        "detection": [{
            "ruleId":
                "ur_ttp_GCP__GlobalSSHKeys_Added",
            "ruleName":
                "GCP Global SSH Keys",
            "urlBackToProduct":
                "https://chronicle.security",
            "alertState":
                "ALERTING",
            "ruleType":
                "SINGLE_EVENT",
            "detectionFields": [{
                "key": "fieldName",
                "value": "fieldValue",
            }],
            "summary":
                "Rule Detection",
            "ruleSet":
                "11c505d4-b424-65e3-d918-1a81232cc76b",
            "ruleSetDisplayName":
                "Admin Action",
            "description":
                "Identifies instances of project-wide SSH keys being added "
                "where there were previously none.",
            "severity":
                "LOW"
        }],
    }

    # Prepare string representations of detection batches that can
    # passed to callback functions.
    mock_detections = []
    for i in range(7):
      mock_detection = mock_detection_template.copy()
      mock_detection["id"] = str(i)  # Not a valid ID format, just for tests.
      mock_detections.append(mock_detection)
    mock_uppercase_detections = []
    for i in range(5):
      mock_detection = mock_uppercase_detection_template.copy()
      mock_detection["id"] = str(i+7)
      mock_uppercase_detections.append(mock_detection)

    mock_detection_batches = [
        # Normal stream responses, which will all be passed to the callback.
        # Some are detection batches with no detections; others are
        # detection batches with detections.
        tuple(([], "2020-12-06T22:39:55.633014925Z")),
        tuple(([mock_detections[:3]], "2020-12-07T22:39:55.633014925Z")),
        tuple(([], "2020-12-08T22:39:55.633014925Z")),
        tuple(([mock_detections[3:4], mock_uppercase_detections[0:3]],
               "2020-12-09T22:39:55.633014925Z")),
        tuple(([], "2020-12-10T22:39:55.633014925Z")),
        tuple(([mock_detections[4:]], "2020-12-11T22:39:55.633014925Z")),
        tuple(([], "2020-12-12T22:39:55.633014925Z")),
        tuple(([mock_uppercase_detections[3:]],
               "2020-12-12T22:39:55.633014925Z")),
        tuple(([], "2020-12-13T22:39:55.633014925Z")),
    ]

    # Serialize detection batches into dumps that will be sent as incremental
    # json responses over the stream.
    detection_batch_dumps = []
    for batch in mock_detection_batches:
      # An initial heartbeat message that confirms connection.
      # It should NOT be passed to the callback.
      if not detection_batch_dumps:
        detection_batch_dumps.append(
            '{"heartbeat": true, "continuationTime": "2020-12-06T22:39:55.633014925Z"}'
        )

      # Desired string format of the detection batch dump:
      #   {"continuationTime": "<continuation time>", "detections": [<list>]}
      detection_batch_dumps.append(
          f'{{"continuationTime": "{batch[1]}",' +
          f' "detections": {json.dumps(batch[0])}}}')

      # Add empty heartbeats in between batches, which will NOT be
      # passed to the callback, which is why we do not put these into
      # the mock_detection_batches list.
      detection_batch_dumps.append('{"heartbeat": true}')
      detection_batch_dumps.append('{"heartbeat": true}')
      detection_batch_dumps.append('{"heartbeat": true}')

    # Make the streamed responses from response.iter_lines() return our
    # detection batches.
    mock_session.post.return_value.__enter__.return_value.iter_lines.side_effect = [
        detection_batch_dumps,
    ]

    # Track the arguments with which the callback gets called.
    callback_call_arguments = []

    def mock_callback(detection_batch_argument):
      nonlocal callback_call_arguments
      callback_call_arguments.append(detection_batch_argument)

    # Call stream_detection_alerts, using our mock callback.
    # A few successful iterations should occur before the
    # retry loop eventually errors out after hitting its retry limit.
    # The loop errors out because we have mocked the streaming response
    # with a finite amount of detection batches, and after those
    # batches are consumed, parsing will hit errors.
    with self.assertRaises(RuntimeError):
      stream_detection_alerts.stream_detection_alerts_in_retry_loop(
          "credentials_file", mock_callback)

    # The callback should be called with the same detections that
    # we mocked our streaming responses with. This also implicitly
    # checks the number of times the callback was called. The
    # heartbeats do not get passed to the callback.
    self.assertEqual(mock_detection_batches, callback_call_arguments)

    # Session should have been initialized more times than
    # the polling loop slept, since the last iteration exits early.
    self.assertGreater(mock_init_session.call_count, mock_sleep.call_count)


if __name__ == "__main__":
  unittest.main()
