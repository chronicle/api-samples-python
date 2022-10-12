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
"""Unit tests for the "create_okta_feed" module."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import create_okta_feed


class CreateFeedTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      create_okta_feed.create_okta_feed(mock_session, "secret_example",
                                        "hostname.example.com", "my feed name")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_feed = {
        "name": "feeds/cf49ebc5-e7bf-4562-8061-cab43cecba35",
        "display_name": "my feed name",
        "details": {
            "logType": "OKTA",
            "feedSourceType": "API",
            "oktaSettings": {
                "authentication": {
                    "headerKeyValues": [{
                        "key": "key_example",
                        "value": "value_example"
                    }]
                }
            },
        },
        "feedState": "PENDING_ENABLEMENT"
    }

    mock_response.json.return_value = expected_feed

    actual_feed = create_okta_feed.create_okta_feed(
        mock_session, "secret_example", "hostname.example.com", "my feed name")
    self.assertEqual(actual_feed, expected_feed)


if __name__ == "__main__":
  unittest.main()
