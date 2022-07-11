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
"""Unit tests for the "list_datatap" module."""

import unittest
import argparse

from unittest import mock

from google.auth.transport import requests

from . import list_datatap


class ListDatatapTest(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = list_datatap.initialize_command_line_args([])
    self.assertEqual(
        actual,
        argparse.Namespace(
            credentials_file=None,
            region="us"))

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_datatap_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_datatap.list_datatap(mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_datatap(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected = {
        "dataTaps": [{
            "customerId": "cccccccc-cccc-cccc-cccc-cccccccccccc",
            "tapId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            "displayName": "tap1",
            "filter": "ALL_UDM_EVENTS",
            "cloudPubsubSink": {
                "topic": "projects/sample-project/topics/sample-topic",
            }
        }]
    }

    mock_response.json.return_value = expected
    actual = list_datatap.list_datatap(mock_session)
    self.assertEqual(actual, expected)


if __name__ == "__main__":
  unittest.main()
  