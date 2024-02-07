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
"""Unit tests for the "query" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import query


class QueryTest(unittest.TestCase):

  # Class variables for ease.
  arguments = {
      "region": "us",
      "project": "123456789101",
      "instance": "test4bb9-878b-11e7-8455-10604b7cb5c1",
  }

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError()
    )

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      query.list_entity_risk_scores(mock_session, **self.arguments)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_query_params(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_response = {
        "entityRiskScores": [
            {
                "entity": {"metadata": {"entityType": "ASSET"}},
                "riskWindow": {
                    "startTime": "2023-08-16T17:45:59.870653094Z",
                    "endTime": "2023-08-23T17:45:59.870654674Z",
                },
                "riskScore": 1000,
                "riskDelta": {"previousRiskScore": 1000},
                "detectionsCount": 3089795,
                "firstDetectionTime": "2023-08-16T17:00:00.232292Z",
                "lastDetectionTime": "2023-08-23T15:59:54.973741Z",
                "entityIndicator": {"assetIpAddress": "127.0.0.1"},
            },
        ],
        "entityCountDistributions": [
            {
                "dailyTimeBucket": {
                    "startTime": "2023-08-16T07:00:00Z",
                    "endTime": "2023-08-17T07:00:00Z",
                },
                "assetEntityCount": 9412,
                "userEntityCount": 2481,
            },
        ],
    }
    mock_response.json.return_value = expected_response

    response = query.list_entity_risk_scores(mock_session, **self.arguments)
    self.assertIn("entityRiskScores", response)
    self.assertIn("entity", response.get("entityRiskScores", [])[0])
    self.assertIn("entityCountDistributions", response)
    self.assertIn(
        "assetEntityCount", response.get("entityCountDistributions", [])[0]
    )
    self.assertIn(
        "userEntityCount", response.get("entityCountDistributions", [])[0]
    )


if __name__ == "__main__":
  unittest.main()
  googletest.main()
