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
"""Unit tests for the "create_udm_events" function."""

import json

import unittest
from unittest import mock

from google.auth.transport import requests

from . import create_udm_events

_test_event = json.dumps([{
    "metadata": {
        "eventTimestamp": "2021-07-01T19:39:08.304950563Z",
        "eventType": "SCAN_HOST",
        "vendorName": "Telemetry4u",
        "productName": "Inspectotron",
    },
    "target": {
        "hostname": "workbox10",
    },
    "securityResult": [{
        "category": ["DATA_AT_REST"],
        "summary": "Personal",
        "description": "Files Labeled: 21+"
    }, {
        "category": ["DATA_AT_REST"],
        "summary": "PCI",
        "description": "Files Labeled: 21+"
    }]
}, {
    "metadata": {
        "eventTimestamp": "2021-07-02T19:39:08.304950563Z",
        "eventType": "SCAN_HOST",
        "vendorName": "Telemetry4u",
        "productName": "Inspectotron",
    },
    "target": {
        "hostname": "workbox10",
    },
    "securityResult": [{
        "category": ["DATA_AT_REST"],
        "summary": "Personal",
        "description": "Files Labeled: 21+"
    }, {
        "category": ["DATA_AT_REST"],
        "summary": "PCI",
        "description": "Files Labeled: 21+"
    }]
}])


class CreateUdmEventTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      create_udm_events.create_udm_events(
          mock_session, "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", _test_event)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)

    create_udm_events.create_udm_events(
        mock_session, "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", _test_event)


if __name__ == "__main__":
  unittest.main()
