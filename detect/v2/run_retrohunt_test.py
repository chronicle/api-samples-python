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
"""Unit tests for the "run_retrohunt" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import run_retrohunt


class RunRetrohuntTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=1)

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      run_retrohunt.run_retrohunt(
          mock_session, "ru_12345678-1234-1234-1234-1234567890ab",
          start_time, end_time)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    expected_rh = {
        "retrohuntId":
            "oh_aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "ruleId":
            "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
        "versionId":
            "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb@v_123456789_12345789",
        "eventStartTime":
            "2021-01-01T00:00:00Z",
        "eventEndTime":
            "2021-01-02T00:00:00Z",
        "retrohuntStartTime":
            "2020-01-01T00:00:00Z",
        "retrohuntEndTime":
            "2020-01-02T00:00:00Z",
        "state":
            "RUNNING",
        "progressPercentage":
            "0.0",
    }
    mock_response.json.return_value = expected_rh

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=1)

    actual_rh = run_retrohunt.run_retrohunt(
        mock_session, "ru_12345678-1234-1234-1234-1234567890ab",
        start_time, end_time)
    self.assertEqual(actual_rh, expected_rh)


if __name__ == "__main__":
  unittest.main()
