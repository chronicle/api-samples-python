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
"""Unit tests for the "get_retrohunt" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import get_retrohunt


class GetRetrohuntTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      get_retrohunt.get_retrohunt(mock_session,
                                  "ru_12345678-1234-1234-1234-1234567890ab",
                                  "oh_87654321-4321-4321-4321-ba0987654321")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_response = {
        "retrohuntId":
            "oh_87654321-4321-4321-4321-ba0987654321",
        "ruleId":
            "ru_12345678-1234-1234-1234-1234567890ab",
        "versionId":
            "ru_12345678-1234-1234-1234-1234567890ab@v_1234567890_123456789",
        "eventStartTime":
            "2021-01-01T00:00:00Z",
        "eventEndTime":
            "2021-01-06T00:00:00Z",
        "retrohuntStartTime":
            "2021-04-28T00:00:00Z",
        "state":
            "RUNNING",
        "progressPercentage":
            19.63,
    }
    mock_response.json.return_value = expected_response

    got_response = get_retrohunt.get_retrohunt(
        mock_session,
        "ru_12345678-1234-1234-1234-1234567890ab",
        "oh_87654321-4321-4321-4321-ba0987654321"
    )
    self.assertEqual(got_response, expected_response)


if __name__ == "__main__":
  unittest.main()
