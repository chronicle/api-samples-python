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
"""Tests for the "get_alert" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import get_alert


class GetAlertTest(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = get_alert.initialize_command_line_args(["--id=1"])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_short(self):
    actual = get_alert.initialize_command_line_args(["-i=1"])
    self.assertIsNotNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      get_alert.get_alert(mock_session, "1")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_get_alert(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    mock_response.json.return_value = {"mock": "json"}
    actual = get_alert.get_alert(mock_session, "1")
    self.assertEqual(actual, {"mock": "json"})


if __name__ == "__main__":
  unittest.main()
