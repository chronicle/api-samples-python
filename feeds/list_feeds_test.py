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
"""Unit tests for the "list_feeds" function."""

import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_feeds


class ListFeedsTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_feeds.list_feeds(mock_session)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_feeds = {
        "feeds": [
            {
                "name": "feeds/19e82867-ab6d-4955-b9c8-bd4aee189439",
                "details": {
                    "logType": "AZURE_AD_CONTEXT",
                    "feedSourceType": "API",
                    "azureAdContextSettings": {}
                },
                "feedState": "INACTIVE"
            },
            {
                "name": "feeds/cdc096a5-93a8-4854-94d9-c05cf0c14d47",
                "details": {
                    "logType": "PAN_PRISMA_CLOUD",
                    "feedSourceType": "API",
                    "panPrismaCloudSettings": {
                        "hostname": "api2.prismacloud.io"
                    }
                },
                "feedState": "ACTIVE"
            },
        ],
    }
    mock_response.json.return_value = expected_feeds

    actual_feeds = list_feeds.list_feeds(mock_session)
    self.assertEqual(actual_feeds, expected_feeds)


if __name__ == "__main__":
  unittest.main()
