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
"""Tests for the "list_iocs" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_iocs


class ListIocsTest(unittest.TestCase):

  def test_initialize_command_line_args_local_time(self):
    actual = list_iocs.initialize_command_line_args(
        ["--start_time=2021-05-07T11:22:33", "--local_time"])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_utc(self):
    actual = list_iocs.initialize_command_line_args(
        ["-ts=2021-05-07T11:22:33Z"])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_page_size(self):
    actual = list_iocs.initialize_command_line_args(
        ["-ts=2021-05-07T11:22:33Z", "--page_size=1000"])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_zero_page_size(self):
    actual = list_iocs.initialize_command_line_args(
        ["-ts=2021-05-07T11:22:33Z", "--page_size=0"])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_large_page_size(self):
    actual = list_iocs.initialize_command_line_args(
        ["-ts=2021-05-07T11:22:33Z", "--page_size=10001"])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_future(self):
    start_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    start_time += datetime.timedelta(days=2)
    actual = list_iocs.initialize_command_line_args(
        [start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ")])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_iocs(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    mock_response.json.return_value = {"mock": "json"}
    actual = list_iocs.list_iocs(mock_session,
                                 datetime.datetime(2021, 5, 7, 11, 22, 33))
    self.assertEqual(actual, {"mock": "json"})


if __name__ == "__main__":
  unittest.main()
