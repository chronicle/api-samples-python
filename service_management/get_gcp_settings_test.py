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
"""Tests for the "get_gcp_settings" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import get_gcp_settings


class GetGCPSettingsTest(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = get_gcp_settings.initialize_command_line_args(
        ["--credentials_file=./foo.json", "--organization_id=123"])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_organization_id_too_big(self):
    invalid_organization_id = 2**64
    actual = get_gcp_settings.initialize_command_line_args(
        [f"--organization_id={invalid_organization_id}"])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_negative_organization_id(self):
    actual = get_gcp_settings.initialize_command_line_args(
        ["--organization_id=-1"])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      get_gcp_settings.get_gcp_settings(mock_session, 123)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)

    get_gcp_settings.get_gcp_settings(mock_session, 123)


if __name__ == "__main__":
  unittest.main()
