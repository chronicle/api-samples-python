# Copyright 2024 Google LLC
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
"""Unit tests for "v1alpha.patch_list" module."""
import unittest
from unittest import mock

from lists.v1alpha import patch_list


class MockArgs:
  pass


class PatchListGetCurrentState(unittest.TestCase):

  def setUp(self):
    super().setUp()
    self.args = MockArgs()
    self.args.project_id = None
    self.args.project_instance = None
    self.args.region = None
    self.args.name = None

  @mock.patch("lists.v1alpha.get_list.get_list")
  def test_extract_values_with_valid_entries(self, mocked_get_list):
    """Test extraction of values when entries are well-formed."""

    mocked_get_list.return_value = {
        "entries": [
            {"value": 1},
            {"value": 2},
            {"value": 3},
        ],
        "revisionCreateTime": None,
    }
    expected = [1, 2, 3], None
    self.assertEqual(patch_list.get_current_state(None, self.args), expected)

  @mock.patch("lists.v1alpha.get_list.get_list")
  def test_get_current_state_without_entries(self, mocked_get_list):
    """Test when "entries" key is missing."""
    mocked_get_list.return_value = {"revisionCreateTime": None}
    expected_result = [], None
    self.assertEqual(patch_list.get_current_state(None, self.args),
                     expected_result)

  @mock.patch("lists.v1alpha.get_list.get_list")
  def test_get_current_state_with_empty_entries(self, mocked_get_list):
    """Test when "entries" is an empty list."""
    mocked_get_list.return_value = {
        "entries": [],
        "revisionCreateTime": None,
    }
    expected_result = [], None
    self.assertEqual(patch_list.get_current_state(None, self.args),
                     expected_result)

  @mock.patch("lists.v1alpha.get_list.get_list")
  def test_get_current_state_with_some_entries_missing_value(self,
                                                             mocked_get_list):
    """Test when some "entries" are missing the "value" key."""
    mocked_get_list.return_value = {
        "entries": [
            {"value": 1},
            {},  # Missing "value"
            {"value": 3},
        ],
        "revisionCreateTime": None,
    }
    with self.assertRaises(KeyError):
      patch_list.get_current_state(None, self.args)


class PatchListExponentialBackoffTest(unittest.TestCase):

  @mock.patch("time.sleep", return_value=None)
  @mock.patch("random.uniform", return_value=0.5)
  def test_wait_time_calculation(self, _, mock_sleep):
    actual_wait_time = patch_list.exponential_backoff(1, 3)
    expected_wait_time = 1.5  # 1 * 1.5
    expected_time_to_sleep = 2.0  # 1 * 1.5 + 0.5
    self.assertEqual(actual_wait_time, expected_wait_time)
    mock_sleep.assert_called_once_with(expected_time_to_sleep)

  @mock.patch("time.sleep", return_value=None)
  def test_function_returns_correct_wait_time_without_jitter(self, mock_sleep):
    # Testing without jitter to simplify calculation
    with unittest.mock.patch("random.uniform", return_value=0):
      wait_time = patch_list.exponential_backoff(1, 3, wait_time=2)
      self.assertEqual(wait_time, 3)  # 2 * 1.5 + 0
      mock_sleep.assert_called_once_with(3.0)

  @mock.patch("time.sleep", return_value=None)
  @mock.patch("random.uniform", return_value=0.5)
  def test_quiet_mode_suppresses_output(self, _, mock_sleep):
    with unittest.mock.patch(
        "sys.stdout",
        new_callable=unittest.mock.MagicMock) as mock_stdout:
      patch_list.exponential_backoff(1, 3, quiet=True)
      mock_stdout.write.assert_not_called()
      mock_sleep.assert_called_once_with(2.0)

  @mock.patch("time.sleep", return_value=None)
  def test_negative_attempt_number(self, mock_sleep):
    """Test handling of a non-positive attempt number, which should ideally return the base wait time."""
    # Attempt is not greater than 0
    wait_time = patch_list.exponential_backoff(0, 3)
    self.assertEqual(wait_time, 1)  # Base wait_time returned directly
    mock_sleep.assert_not_called()


class PatchListOpUpdateContentLinesTest(unittest.TestCase):

  def test_add_with_duplicates(self):
    curr_list = ["item1", "item2"]
    content_lines = ["item2", "item3"]
    result = patch_list.op_update_content_lines("add",
                                                curr_list, content_lines)
    self.assertEqual(result, ["item1", "item2", "item3"])

  def test_remove(self):
    curr_list = ["item1", "item2", "item3"]
    content_lines = ["item2"]  # Items to remove
    result = patch_list.op_update_content_lines("remove",
                                                curr_list, content_lines)
    self.assertEqual(result, ["item1", "item3"])

  def test_no_change_no_force(self):
    curr_list = ["item1"]
    content_lines = ["item1"]
    with self.assertRaises(SystemExit) as cm:  # Expect the exit behavior
      patch_list.op_update_content_lines("add",
                                         curr_list, content_lines, force=False)
    self.assertEqual(cm.exception.code, 0)

  def test_no_change_force(self):
    curr_list = ["item1"]
    content_lines = ["item1"]
    result = patch_list.op_update_content_lines("add",
                                                curr_list, content_lines,
                                                force=True)
    self.assertEqual(result, ["item1"])


class PatchListReadContentLinesTest(unittest.TestCase):

  def helper(self, mock_file_content, expected_result):
    with unittest.mock.patch(
        "builtins.open",
        unittest.mock.mock_open(read_data=mock_file_content)) as mocked_file:
      # Call the function with the mocked file handle
      file_handle = open("dummy_file", "r")  # mocked file name doesn't matter
      result = patch_list.read_content_lines(file_handle)
      # Assert that the read content matches the expected result
      self.assertEqual(result, expected_result)
      # Ensure that seek(0) was called on the file handle to rewind it
      file_handle.seek.assert_called_with(0)
      # Ensure the file was opened in read mode
      mocked_file.assert_called_with("dummy_file", "r")

  def test_three_entries(self):
    # Mock content to be read
    mock_file_content = "Line 1\nLine 2\nLine 3"
    # Expected result after stripping
    expected_result = ["Line 1", "Line 2", "Line 3"]
    self.helper(mock_file_content, expected_result)

  def test_three_crlf_entries(self):
    mock_file_content = "Line 1\r\nLine 2\r\nLine 3"
    expected_result = ["Line 1", "Line 2", "Line 3"]
    self.helper(mock_file_content, expected_result)

  def test_zero_entries(self):
    mock_file_content = ""
    expected_result = []
    self.helper(mock_file_content, expected_result)


if __name__ == "__main__":
  unittest.main()
