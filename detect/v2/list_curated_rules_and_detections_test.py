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
"""Unit tests for the "list_curated_rules_and_detections" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_curated_rules_and_detections


class ListCuratedRulesAndDetectionsTest(unittest.TestCase):

  @mock.patch("time.sleep", return_value=None)
  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session, mock_sleep):
    # Both list_curated_rules and list_curated_rule_detections succeed.
    type(mock_response).status_code = mock.PropertyMock(side_effect=[200, 200])
    mock_response.raise_for_status.side_effect = [None, None]

    # Response for ListCuratedRules.
    expected_rule = {
        "ruleId": "ur_sample_rule",
        "ruleName": "Sample Rule",
        "severity": "Info",
        "ruleType": "SINGLE_EVENT",
        "precision": "PRECISE",
        "tactics": ["TA0042",],
        "techniques": ["T1595.001",],
        "updateTime": "2023-01-01T00:00:00Z",
        "ruleSet": "87654321-4321-4321-4321-ba0987654321",
        "description": "Sample Rule Description",
    }

    # Response for ListCuratedRuleDetections.
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
    mock_response.json.side_effect = [{
        "curatedRules": [expected_rule],
    }, {
        "curatedRuleDetections": [expected_detection],
        "nextPageToken": expected_page_token,
    }]
    mock_session.request.return_value = mock_response

    responses = list_curated_rules_and_detections.list_curated_rules_and_detections(
        mock_session, page_size=1)
    self.assertEqual(len(responses), 1)
    # There should be one 3-tuple in the list.
    self.assertEqual(responses[0][0], rule_id)
    self.assertEqual(responses[0][1], [expected_detection])
    self.assertEqual(responses[0][2], expected_page_token)
    # Sleep should be called only once since there is only one call to
    # ListCuratedRuleDetections.
    self.assertEqual(mock_sleep.call_count, 1)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_curated_rules_error(self, mock_response, mock_session):
    # list_curated_rules fails causing an overall early failure.
    type(mock_response).status_code = mock.PropertyMock(side_effect=[400])
    mock_response.raise_for_status.side_effect = [
        requests.requests.exceptions.HTTPError()
    ]
    mock_response.json.side_effect = [None]
    mock_session.request.return_value = mock_response

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_curated_rules_and_detections.list_curated_rules_and_detections(
          mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_curated_rule_detections_error(self, mock_response,
                                              mock_session):
    # list_curated_rules succeeds but list_curated_rule_detections fails.
    type(mock_response).status_code = mock.PropertyMock(side_effect=[200, 400])
    mock_response.raise_for_status.side_effect = [
        None, requests.requests.exceptions.HTTPError()
    ]

    # Response for ListCuratedRules.
    expected_rule = {
        "ruleId": "ur_sample_rule",
        "ruleName": "Sample Rule",
        "severity": "Info",
        "ruleType": "SINGLE_EVENT",
        "precision": "PRECISE",
        "tactics": ["TA0042",],
        "techniques": ["T1595.001",],
        "updateTime": "2023-01-01T00:00:00Z",
        "ruleSet": "87654321-4321-4321-4321-ba0987654321",
        "description": "Sample Rule Description",
    }
    mock_response.json.side_effect = [{
        "curatedRules": [expected_rule],
    }, None]
    mock_session.request.return_value = mock_response

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_curated_rules_and_detections.list_curated_rules_and_detections(
          mock_session)


if __name__ == "__main__":
  unittest.main()
