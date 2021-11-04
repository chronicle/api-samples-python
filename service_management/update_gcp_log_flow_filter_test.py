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
"""Tests for the "update_gcp_log_flow_filter" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import update_gcp_log_flow_filter

SAMPLE_FILTER_ID = "00000000-0000-0000-0000-000000000000"

DEFAULT_FILTER_EXPRESSION = (
    "log_id(\"dns.googleapis.com/dns_queries\") OR "
    "log_id(\"cloudaudit.googleapis.com/activity\") OR "
    "log_id(\"cloudaudit.googleapis.com/system_event\")")


class UpdateGCPLogFlowFilter(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = update_gcp_log_flow_filter.initialize_command_line_args([
        "--credentials_file=./foo.json", "--organization_id=123",
        f"--filter_id={SAMPLE_FILTER_ID}",
        f"--filter_expression={DEFAULT_FILTER_EXPRESSION}"
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_organization_id_too_big(self):
    invalid_organization_id = 2**64
    actual = update_gcp_log_flow_filter.initialize_command_line_args([
        f"--organization_id={invalid_organization_id}",
        f"--filter_id={SAMPLE_FILTER_ID}",
        f"--filter_expression={DEFAULT_FILTER_EXPRESSION}"
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_negative_organization_id(self):
    actual = update_gcp_log_flow_filter.initialize_command_line_args([
        "--organization_id=-1", f"--filter_id={SAMPLE_FILTER_ID}",
        f"--filter_expression={DEFAULT_FILTER_EXPRESSION}"
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_invalid_filter_id(self):
    actual = update_gcp_log_flow_filter.initialize_command_line_args([
        "--organization_id=123", "--filter_id=123",
        f"--filter_expression={DEFAULT_FILTER_EXPRESSION}"
    ])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      update_gcp_log_flow_filter.update_gcp_log_flow_filter(
          mock_session, 123, SAMPLE_FILTER_ID, DEFAULT_FILTER_EXPRESSION)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)

    update_gcp_log_flow_filter.update_gcp_log_flow_filter(
        mock_session, 123, SAMPLE_FILTER_ID, DEFAULT_FILTER_EXPRESSION)


if __name__ == "__main__":
  unittest.main()
