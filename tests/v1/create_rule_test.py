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
"""Unit tests for the "create_rule" module."""

import unittest
from unittest import mock

from google.auth.transport import requests
from samples.v1 import create_rule


class CreateRuleTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_content_sanity_check(self, mock_session):
    with self.assertRaises(ValueError):
      create_rule.create_rule(mock_session, "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      create_rule.create_rule(mock_session, "new rule content")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_rule_id = "ru_12345678-1234-1234-1234-1234567890ab"
    mock_response.json.return_value = {"ruleId": expected_rule_id}

    actual_rule_id = create_rule.create_rule(mock_session, "new rule content")
    self.assertEqual(actual_rule_id, expected_rule_id)


if __name__ == "__main__":
  unittest.main()
