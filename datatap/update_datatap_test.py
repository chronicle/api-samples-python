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
"""Unit tests for the "update_datatap" module."""

import unittest
import argparse

from unittest import mock

from google.auth.transport import requests

from . import update_datatap


class UpdateDatatapTest(unittest.TestCase):

  def test_initialize_command_line_args(self):
    actual = update_datatap.initialize_command_line_args([
        "--name=sink1", "--topic=projects/sample-project/topics/sample-topic",
        "--filter=ALL_UDM_EVENTS",
        "--serialization_format=JSON",
        "--tapId=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    ])
    self.assertEqual(
        actual,
        argparse.Namespace(
            credentials_file=None,
            name="sink1",
            topic="projects/sample-project/topics/sample-topic",
            filter="ALL_UDM_EVENTS",
            serialization_format="JSON",
            tapId="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
            region="us"))

  def test_initialize_command_line_args_filter_type(self):
    actual = update_datatap.initialize_command_line_args([
        "--name=sink1", "--topic=projects/sample-project/topics/sample-topic",
        "--filter=INVALID_FILTER",
        "--tapId=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    ])
    self.assertIsNone(actual)

  def test_initialize_command_line_args_tap_id_missing(self):
    with self.assertRaises(SystemExit) as error:
      update_datatap.initialize_command_line_args([
          "--name=sink1",
          "--topic=projects/sample-project/topics/sample-topic",
          "--filter=ALL_UDM_EVENTS",
      ])
    self.assertEqual(error.exception.code, 2)

  def test_initialize_command_line_args_filter_missing(self):
    with self.assertRaises(SystemExit) as error:
      update_datatap.initialize_command_line_args([
          "--name=sink1",
          "--topic=projects/sample-project/topics/sample-topic",
          "--tapId=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
      ])
    self.assertEqual(error.exception.code, 2)

  def test_initialize_command_line_args_name_missing(self):
    with self.assertRaises(SystemExit) as error:
      update_datatap.initialize_command_line_args([
          "--topic=projects/sample-project/topics/sample-topic",
          "--tapId=aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
          "--filter=ALL_UDM_EVENTS",
      ])
    self.assertEqual(error.exception.code, 2)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_update_datatap_error(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=400)
    mock_response.raise_for_status.side_effect = (
        requests.requests.exceptions.HTTPError())

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      update_datatap.update_datatap(mock_session, "", "", "", "", "")

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_update_datatap(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(return_value=200)
    name = "tap1"
    topic = "projects/sample-project/topics/sample-topic"
    filter_type = "ALL_UDM_EVENTS"
    serialization_format = "JSON"
    tap_id = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
    expected = {
        "customerId": "cccccccc-cccc-cccc-cccc-cccccccccccc",
        "tapId": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "displayName": "tap1",
        "filter": "ALL_UDM_EVENTS",
        "serializationFormat": "JSON",
        "cloudPubsubSink": {
            "topic": "projects/sample-project/topics/sample-topic",
        }
    }

    mock_response.json.return_value = expected
    actual = update_datatap.update_datatap(mock_session, name, topic,
                                           filter_type, serialization_format,
                                           tap_id)
    self.assertEqual(actual, expected)


if __name__ == "__main__":
  unittest.main()

