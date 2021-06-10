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
"""Unit tests for the "list_errors" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_errors


class ListErrorsTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_errors.list_errors(mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_page_size(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_error = {
        "category": "RULES_EXECUTION_ERROR",
        "errorId": "ed_12345678-1234-1234-1234-1234567890ab",
        "errorTime": "2020-12-09T16:00:00Z",
        "ruleExecution": {
            "ruleId":
                "ru_12345678-1234-1234-1234-1234567890ab",
            "versionId":
                "ru_12345678-1234-1234-1234-1234567890ab@v_100000_000000",
            "windowEndTime":
                "2020-12-09T16:00:00Z",
            "windowStartTime":
                "2020-12-09T15:00:00Z"
        },
        "text": "rule error text"
                "line: 15 \n"
                "column: 37-74 "
    }
    expected_page_token = "page token here"
    mock_response.json.return_value = {
        "errors": [expected_error],
        "nextPageToken": expected_page_token,
    }

    errors, next_page_token = list_errors.list_errors(mock_session)
    self.assertEqual(len(errors), 1)
    self.assertEqual(errors[0], expected_error)
    self.assertEqual(next_page_token, expected_page_token)


if __name__ == "__main__":
  unittest.main()
