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
"""Unit tests for the "get_error" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import get_error


class GetErrorTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      get_error.get_error(mock_session, "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    error_id = "ed_12345678-1234-1234-1234-1234567890ab"
    version_id = "ru_12345678-1234-1234-1234-1234567890ab@v_100000_000000"
    expected_error = {
        "errorId": error_id,
        "text": "something went wrong",
        "category": "RULES_EXECUTION_ERROR",
        "errorTime": "2020-11-05T00:00:00Z",
        "metadata": {
            "ruleExecution": {
                "windowStartTime": "2020-11-05T00:00:00Z",
                "windowEndTime": "2020-11-05T01:00:00Z",
                "ruleId": "ru_12345678-1234-1234-1234-1234567890ab",
                "versionId": version_id,
            },
        },
    }
    mock_response.json.return_value = expected_error

    error = get_error.get_error(mock_session, error_id)
    self.assertEqual(error, expected_error)


if __name__ == "__main__":
  unittest.main()
