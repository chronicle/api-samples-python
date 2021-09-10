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
"""Tests for the "list_alerts" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_alerts


class ListAlertsTest(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = list_alerts.initialize_command_line_args(["--page_size=5"])
    self.assertIsNotNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_alerts.list_alerts(mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_alerts(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)

    expected_alert = {"alertId": "1"}
    expected_page_token = "page token here"
    mock_response.json.return_value = {
        "uppercaseAlerts": [expected_alert],
        "nextPageToken": expected_page_token,
    }

    alerts, next_page_token = list_alerts.list_alerts(mock_session)
    self.assertCountEqual(alerts, [expected_alert])
    self.assertEqual(next_page_token, expected_page_token)


if __name__ == "__main__":
  unittest.main()
