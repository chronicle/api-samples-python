# Copyright 2020 Google LLC
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
"""Unit tests for the "enable_live_rule" module."""

import unittest
from unittest import mock

from google.auth.transport import requests
from samples.v1 import enable_live_rule


class EnableLiveRuleTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_rule_id_sanity_check(self, mock_session):
    with self.assertRaises(ValueError):
      enable_live_rule.enable_live_rule(mock_session, "invalid-rule-id")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      enable_live_rule.enable_live_rule(
          mock_session, "ru_12345678-1234-1234-1234-1234567890ab")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_operation_id = "rulejob_jo_12345678-1234-1234-1234-1234567890ab"
    mock_response.json.return_value = {
        "name": "operations/" + expected_operation_id
    }

    actual_operation_id = enable_live_rule.enable_live_rule(
        mock_session, "ru_12345678-1234-1234-1234-1234567890ab")
    self.assertEqual(actual_operation_id, expected_operation_id)


if __name__ == "__main__":
  unittest.main()
