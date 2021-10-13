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
"""Tests for the "list_asset_events" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import list_asset_events


class ListAssetEventsTest(unittest.TestCase):

  def test_initialize_command_line_args_hostname_local_time(self):
    actual = list_asset_events.initialize_command_line_args([
        "--hostname=foobar",
        "--start_time=2021-10-04T00:00:00",
        "--end_time=2021-10-05T00:00:00",
        "--ref_time=2021-10-04T12:00:00",
        "--local_time",
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_ip_utc(self):
    actual = list_asset_events.initialize_command_line_args([
        "--ip_address=127.0.0.1",
        "--start_time=2021-10-04T00:00:00Z",
        "--end_time=2021-10-05T00:00:00Z",
        "--ref_time=2021-10-04T12:00:00Z",
    ])
    self.assertIsNotNone(actual)

  def test_initialize_command_line_args_zero_asset_indicators(self):
    end_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    ref_time = end_time - datetime.timedelta(days=1)
    start_time = ref_time - datetime.timedelta(days=1)
    actual = list_asset_events.initialize_command_line_args([
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        ref_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_two_asset_indicators(self):
    end_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    ref_time = end_time - datetime.timedelta(days=1)
    start_time = ref_time - datetime.timedelta(days=1)
    actual = list_asset_events.initialize_command_line_args([
        "-n=hostname",
        "-i=172.168.0.1",
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        ref_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_future_start_time(self):
    ref_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    start_time = ref_time + datetime.timedelta(hours=1)
    end_time = start_time + datetime.timedelta(hours=1)
    actual = list_asset_events.initialize_command_line_args([
        "-n=hostname",
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        ref_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_future_reference_time(self):
    start_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    start_time -= datetime.timedelta(hours=1)
    ref_time = start_time + datetime.timedelta(hours=2)
    end_time = ref_time + datetime.timedelta(hours=1)
    actual = list_asset_events.initialize_command_line_args([
        "-i=172.168.0.1",
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        ref_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_empty_time_range(self):
    start_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    start_time -= datetime.timedelta(days=2)
    actual = list_asset_events.initialize_command_line_args([
        "-m=172.168.0.1",
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        start_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        start_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_negative_time_range(self):
    start_time = datetime.datetime.utcnow().astimezone(datetime.timezone.utc)
    start_time -= datetime.timedelta(days=2)
    ref_time = start_time - datetime.timedelta(days=2)
    end_time = ref_time - datetime.timedelta(days=2)
    actual = list_asset_events.initialize_command_line_args([
        "-n=hostname",
        start_time.strftime("-ts=%Y-%m-%dT%H:%M:%SZ"),
        end_time.strftime("-te=%Y-%m-%dT%H:%M:%SZ"),
        ref_time.strftime("-tr=%Y-%m-%dT%H:%M:%SZ"),
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_negative_page_size(self):
    actual = list_asset_events.initialize_command_line_args([
        "--ip_address=127.0.0.1",
        "--start_time=2021-10-04T00:00:00Z",
        "--end_time=2021-10-05T00:00:00Z",
        "--ref_time=2021-10-04T12:00:00Z",
        "--page_size=-1",
    ])
    self.assertIsNone(actual)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_list_asset_events(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    mock_response.json.return_value = {"uri": ["http://foo.com"]}
    actual = list_asset_events.list_asset_events(
        mock_session, "product_id", "CS:12345",
        datetime.datetime(2021, 5, 7, 11, 22, 33),
        datetime.datetime(2021, 5, 9, 11, 22, 33),
        datetime.datetime(2021, 5, 8, 11, 22, 33))
    self.assertEqual(actual, ([], False, "http://foo.com"))

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_http_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      list_asset_events.list_asset_events(
          mock_session, "product_id", "CS:12345",
          datetime.datetime(2021, 5, 7, 11, 22, 33),
          datetime.datetime(2021, 5, 9, 11, 22, 33),
          datetime.datetime(2021, 5, 8, 11, 22, 33))


if __name__ == "__main__":
  unittest.main()
