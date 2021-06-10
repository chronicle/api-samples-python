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
"""Unit tests for the "list_retrohunts" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_retrohunts


class ListRetrohuntsTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_retrohunts.list_retrohunts(
          mock_session, "ru_12345678-1234-1234-1234-1234567890ab", "RUNNING",
          100, "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_page_size(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_retrohunt = {
        "retrohuntId":
            "oh_aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "ruleId":
            "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "versionId":
            "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb@v_123456789_12345789",
        "eventStartTime":
            "2021-01-01T00:00:00Z",
        "eventEndTime":
            "2021-01-02T00:00:00Z",
        "retrohuntStartTime":
            "2020-01-01T00:00:00Z",
        "retrohuntEndTime":
            "2020-01-02T00:00:00Z",
        "state":
            "RUNNING",
        "progressPercentage":
            "0.0",
    }
    expected_page_token = "page token here"
    mock_response.json.return_value = {
        "retrohunts": [expected_retrohunt],
        "nextPageToken": expected_page_token,
    }

    retrohunts, next_page_token = list_retrohunts.list_retrohunts(
        mock_session, "ru_12345678-1234-1234-1234-1234567890ab", "RUNNING")
    self.assertEqual(len(retrohunts), 1)
    self.assertEqual(retrohunts[0], expected_retrohunt)
    self.assertEqual(next_page_token, expected_page_token)


if __name__ == "__main__":
  unittest.main()
