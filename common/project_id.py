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
"""Support for Project ID for v1alpha Chronicle API calls."""
import argparse


def add_argument_project_id(parser: argparse.ArgumentParser):
  """Adds a shared command-line argument to all the sample modules."""
  parser.add_argument(
      "-p", "--project_id", type=str, required=True,
      help="Your BYOP, project id",
  )
