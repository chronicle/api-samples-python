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
"""Unit tests for the "run_rule_and_wait" module."""

import datetime
import unittest
from unittest import mock

from google.auth.transport import requests
from samples.v1 import run_rule_and_wait


class RunRuleAndWaitTest(unittest.TestCase):

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_rule_id_sanity_check(self, mock_session):
    event_end_time = datetime.datetime.now()
    event_start_time = event_end_time - datetime.timedelta(hours=1)

    with self.assertRaises(ValueError):
      run_rule_and_wait.run_rule_and_wait(mock_session, "invalid-rule-id",
                                          event_start_time, event_end_time)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  def test_times_sanity_check(self, mock_session):
    event_start_time = datetime.datetime.now()
    event_end_time = event_start_time - datetime.timedelta(hours=1)

    with self.assertRaises(ValueError):
      run_rule_and_wait.run_rule_and_wait(
          mock_session, "ru_12345678-1234-1234-1234-1234567890ab",
          event_start_time, event_end_time)

  @mock.patch.object(requests, "AuthorizedSession", autospec=True)
  @mock.patch.object(requests.requests, "Response", autospec=True)
  def test_happy_path(self, mock_response, mock_session):
    mock_session.request.return_value = mock_response
    # 1. run_rule success, 2. get_operation success, 3. list_results success.
    type(mock_response).status_code = mock.PropertyMock(
        side_effect=[200, 200, 200])
    mock_response.raise_for_status.side_effect = [None, None, None]
    expected_results = [{"match": {}}]
    mock_response.json.side_effect = [
        # JSON result of run_rule().
        {
            "name":
                "operations/rulejob_jo_12345678-1234-1234-1234-1234567890ab",
        },
        # JSON result of get_operation().
        {
            "name":
                "operations/rulejob_jo_12345678-1234-1234-1234-1234567890ab",
            "done":
                True,
            "metadata": {
                "ruleId": None,
                "@type": None,
            },
        },
        # JSON result of list_results().
        {
            "results": expected_results,
        },
    ]

    event_end_time = datetime.datetime.now()
    event_start_time = event_end_time - datetime.timedelta(hours=1)

    actual_results = run_rule_and_wait.run_rule_and_wait(
        mock_session, "ru_12345678-1234-1234-1234-1234567890ab",
        event_start_time, event_end_time)
    self.assertEqual(actual_results, expected_results)


if __name__ == "__main__":
  unittest.main()
