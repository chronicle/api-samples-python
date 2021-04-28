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
#
"""Unit tests for the "list_detections" module."""

import unittest
from unittest import mock

from google.auth.transport import requests
from . import list_detections


class ListDetectionsTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_detections.list_detections(mock_session, "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_page_size(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    version_id = "ru_12345678-1234-1234-1234-1234567890ab@v_100000_000000"
    expected_detection = {
        "id": "de_12345678-1234-1234-1234-1234567890ab",
        "type": "RULE_DETECTION",
        "createdTime": "2020-11-05T12:00:00Z",
        "detectionTime": "2020-11-05T01:00:00Z",
        "timeWindow": {
            "startTime": "2020-11-05T00:00:00Z",
            "endTime": "2020-11-05T01:00:00Z",
        },
        "detection": [
            {
                "ruleId": "ru_12345678-1234-1234-1234-1234567890ab",
                "ruleName": "rule content",
                "ruleVersion": version_id,
                "urlBackToProduct": "https://chronicle.security",
                "alertState": "ALERTING",
                "ruleType": "MULTI_EVENT",
                "detectionFields": [
                    {
                        "key": "fieldName",
                        "value": "fieldValue",
                    }
                ]
            }
        ],
    }
    expected_page_token = "page token here"
    mock_response.json.return_value = {
        "detections": [expected_detection],
        "nextPageToken": expected_page_token,
    }

    detections, next_page_token = list_detections.list_detections(
        mock_session, version_id)
    self.assertEqual(len(detections), 1)
    self.assertEqual(detections[0], expected_detection)
    self.assertEqual(next_page_token, expected_page_token)


if __name__ == "__main__":
  unittest.main()
