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
"""Unit tests for the "run_retrohunt_and_wait" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests

from . import run_retrohunt_and_wait as wait


class RunRetrohuntAndWaitTest(unittest.TestCase):

  @mock.patch("time.sleep", return_value=None)
  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session, mock_sleep):
    # run retrohunt, wait retrohunt, list detections, all success.
    type(mock_response).status_code = mock.PropertyMock(
        side_effect=[200, 200, 200])
    mock_response.raise_for_status.side_effect = [None, None, None]
    rule_id = "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    version_id = f"{rule_id}@v_123456789_12345789"
    # Response for RunRetrohunt
    running_rh = {
        "retrohuntId":
            "oh_aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "ruleId": rule_id,
        "versionId": version_id,
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
    # Response for GetRetrohunt
    completed_rh = running_rh.copy()
    completed_rh["state"] = "DONE"
    completed_rh["progressPercentage"] = "100.0"

    # Response for ListDetections
    expected_detection = {
        "id": "de_12345678-1234-1234-1234-1234567890ab",
        "type": "RULE_DETECTION",
        "createdTime": "2020-11-05T12:00:00Z",
        "detectionTime": "2020-11-05T01:00:00Z",
        "timeWindow": {
            "startTime": "2020-11-05T00:00:00Z",
            "endTime": "2020-11-05T01:00:00Z",
        },
        "detection": [
            {
                "ruleId": "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
                "ruleName": "rule content",
                "ruleVersion": version_id,
                "urlBackToProduct": "https://chronicle.security",
                "alertState": "ALERTING",
                "ruleType": "MULTI_EVENT",
                "detectionFields": [
                    {
                        "key": "fieldName",
                        "value": "fieldValue",
                    }
                ]
            }
        ],
    }
    expected_page_token = "page token"
    mock_response.json.side_effect = [
        running_rh, completed_rh, {
            "detections": [expected_detection],
            "nextPageToken": expected_page_token,
        }
    ]
    mock_session.request.return_value = mock_response

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=1)

    got_detections, next_page_token = wait.run_retrohunt_and_wait(
        mock_session, rule_id, start_time, end_time)
    self.assertEqual(len(got_detections), 1)
    self.assertEqual(got_detections[0], expected_detection)
    self.assertEqual(next_page_token, expected_page_token)
    # Sleep should be called only once.
    self.assertEqual(mock_sleep.call_count, 1)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_retrohunt_not_complete(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(
        side_effect=[200, 200, 200, 200])
    rule_id = "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    version_id = f"{rule_id}@v_123456789_12345789"
    # Response for RunRetrohunt.
    running_rh = {
        "retrohuntId":
            "oh_aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "ruleId": rule_id,
        "versionId": version_id,
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

    # We'll call run_retrohunt_and_wait with sleep_secounds=2,
    # timeout_minutes 0.05(=3sec). With this setup, we make 2 GetRetrohunt calls
    # and exit the loop.
    # Flow in the loop will be: sleep 2sec -> call GetRetrohunt ->
    #   about 2.5 secs has passed -> sleep 2sec -> call GetRetrohunt

    # Responses for the two GetRetrohunt calls.
    running_rh2 = running_rh.copy()
    running_rh2["progressPercentage"] = "10.0"
    running_rh3 = running_rh.copy()
    running_rh3["progressPercentage"] = "20.0"

    # Order of reponses
    # 1. RunRetrohunt
    # 2. 1st call for GetRetrohunt
    # 3. 2nd call for GetRetrohunt
    # 4. Empty response for CancelRetrohunt
    mock_response.json.side_effect = [
        running_rh, running_rh2, running_rh3, None
    ]
    mock_response.raise_for_status.side_effect = ([None, None, None, None])

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=1)

    with self.assertRaises(TimeoutError):
      wait.run_retrohunt_and_wait(
          mock_session,
          rule_id,
          start_time,
          end_time,
          sleep_seconds=2,
          timeout_minutes=0.05)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_wait_retrohunt_timeout_cancel_retrohunt_error(
      self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    type(mock_response).status_code = mock.PropertyMock(
        side_effect=[200, 200, 400])
    rule_id = "ru_bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
    version_id = f"{rule_id}@v_123456789_12345789"
    # Response for RunRetrohunt.
    running_rh = {
        "retrohuntId":
            "oh_aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "ruleId": rule_id,
        "versionId": version_id,
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
    # Response for GetRetrohunt.
    running_rh2 = running_rh.copy()
    running_rh2["progressPercentage"] = "10.0"
    # We'll call run_retrohunt_and_wait with sleep_seconds=2,
    # timeout_minutes=0.02(=1.2sec), so we make only 1 GetRetrohunt call.
    # Call flow will be RunRetrohunt, GetRetrohunt, CancelRetrohunt.
    mock_response.json.side_effect = [running_rh, running_rh2, None]
    # CancelRetrohunt will fail.
    mock_response.raise_for_status.side_effect = (
        [None,
         None,
         requests.requests.exceptions.HTTPError()])

    end_time = datetime.datetime.now()
    start_time = end_time - datetime.timedelta(hours=1)

    with self.assertRaises(requests.requests.exceptions.HTTPError):
      wait.run_retrohunt_and_wait(
          mock_session,
          rule_id,
          start_time,
          end_time,
          sleep_seconds=2,
          timeout_minutes=0.02)


if __name__ == "__main__":
  unittest.main()
