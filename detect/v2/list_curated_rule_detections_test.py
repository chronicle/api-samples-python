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
"""Unit tests for the "list_curated_rule_detections" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_curated_rule_detections


class ListCuratedRuleDetectionsTest(unittest.TestCase):

  def test_initialize_command_line_args_rule_id(self):
    actual = list_curated_rule_detections.initialize_command_line_args([
        "--rule_id=ur_sample_rule",
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_with_valid_parameters(self):
    actual = list_curated_rule_detections.initialize_command_line_args([
        "--rule_id=ur_sample_rule",
        "--start_time=2023-01-04T00:00:00",
        "--end_time=2023-01-05T00:00:00",
        "--page_size=1000",
        "--alert_state=ALERTING",
        "--list_basis=CREATED_TIME",
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_future_start_time(self):
    start_time = datetime.datetime.now().astimezone(
        datetime.timezone.utc) + datetime.timedelta(hours=1)
    end_time = start_time + datetime.timedelta(hours=1)
    actual = list_curated_rule_detections.initialize_command_line_args([
        "--rule_id=ur_sample_rule",
        start_time.strftime("-st=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-et=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_end_time_before_start_time(self):
    actual = list_curated_rule_detections.initialize_command_line_args([
        "--rule_id=ur_sample_rule",
        "--start_time=2023-01-05T00:00:00",
        "--end_time=2023-01-04T00:00:00",
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_invalid_alert_state(self):
    actual = list_curated_rule_detections.initialize_command_line_args(
        ["--rule_id=ur_sample_rule", "--alert_state=ALERT"])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_invalid_list_basis(self):
    actual = list_curated_rule_detections.initialize_command_line_args(
        ["--rule_id=ur_sample_rule", "--list_basis=COMMIT_TIME"])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_curated_rule_detections.list_curated_rule_detections(
          mock_session, "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_page_size(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    rule_id = "ur_sample_rule"
    expected_detection = {
        "id":
            "de_12345678-1234-1234-1234-1234567890ab",
        "type":
            "GCTI_FINDING",
        "createdTime":
            "2023-01-01T12:00:00Z",
        "detectionTime":
            "2023-01-01T01:00:00Z",
        "tags": [
            "TA0043",
            "T1595.001",
        ],
        "timeWindow": {
            "startTime": "2023-01-01T00:00:00Z",
            "endTime": "2023-01-01T01:00:00Z",
        },
        "detection": [{
            "ruleId": "ur_sample_rule",
            "ruleName": "Sample Rule",
            "summary": "Sample Rule Summary",
            "description": "Sample Rule Description",
            "urlBackToProduct": "https://chronicle.security",
            "alertState": "ALERTING",
            "ruleType": "MULTI_EVENT",
            "detectionFields": [{
                "key": "fieldName",
                "value": "fieldValue",
            }],
            "ruleSet": "87654321-4321-4321-4321-ba0987654321",
            "ruleSetDisplayName": "Rule Set Display Name"
        }],
    }
    expected_page_token = "page token here"
    mock_response.json.return_value = {
        "curatedRuleDetections": [expected_detection],
        "nextPageToken": expected_page_token,
    }

    detections, next_page_token = list_curated_rule_detections.list_curated_rule_detections(
        mock_session, rule_id)
    self.assertEqual(len(detections), 1)
    self.assertEqual(detections[0], expected_detection)
    self.assertEqual(next_page_token, expected_page_token)


if __name__ == "__main__":
  unittest.main()
