# Copyright 2022 Google LLC
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
"""Tests for the "udm_search" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import udm_search


class UDMSearchTest(unittest.TestCase):

  def test_initialize_command_line_args_utc(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2022-08-01T00:00:00", "--end_time=2022-08-01T01:00:00"
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_local_time(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2022-08-01T00:00:00", "--end_time=2022-08-01T01:00:00",
        "--local_time"
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_limit(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2022-08-01T00:00:00", "--end_time=2022-08-01T01:00:00",
        "--limit=100"
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_invalid_limit(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2022-08-01T00:00:00", "--end_time=2022-08-01T01:00:00",
        "--limit=100000"
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_invalid_start_time(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2100-08-01T00:00:00", "--end_time=2022-08-01T01:00:00"
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_invalid_end_time(self):
    actual = udm_search.initialize_command_line_args([
        "--query=metadata.event_type=\"NETWORK_CONNECTION\"",
        "--start_time=2022-08-01T00:00:00", "--end_time=2022-07-01T01:00:00"
    ])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_udm_search(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    mock_response.json.return_value = {"mock": "json"}
    actual = udm_search.udm_search(mock_session, "principal.ip=\"10.1.2.3\"",
                                   datetime.datetime(2022, 8, 1, 00, 00, 00),
                                   datetime.datetime(2022, 8, 2, 0, 0, 0))
    self.assertEqual(actual, {"mock": "json"})


if __name__ == "__main__":
  unittest.main()
