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
"""Unit tests for the "list_rules" module."""

import unittest
from unittest import mock

from google.auth.transport import requests
from samples.v1 import list_rules


class ListRulesTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_rules.list_rules(mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_with_size_limit(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_rule = {
        "ruleId": "ru_12345678-1234-1234-1234-1234567890ab",
        "rule": "rule content",
    }
    mock_response.json.return_value = {"rules": [expected_rule]}

    rules = list_rules.list_rules(mock_session)
    self.assertEqual(len(rules), 1)
    self.assertEqual(rules[0], expected_rule)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path_without_size_limit(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_rule = {
        "ruleId": "ru_12345678-1234-1234-1234-1234567890ab",
        "rule": "rule content",
    }
    mock_response.json.return_value = {"rules": [expected_rule]}

    rules = list_rules.list_rules(mock_session, 1)
    self.assertEqual(len(rules), 1)
    self.assertEqual(rules[0], expected_rule)


if __name__ == "__main__":
  unittest.main()
