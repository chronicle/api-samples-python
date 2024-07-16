#!/usr/bin/env python3

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
r"""Executable and reusable sample for updating an Alert.

Usage:
  python -m alerts.v1alpha.update_alert \
    --project_id=<PROJECT_ID>   \
    --project_instance=<PROJECT_INSTANCE> \
    --alert_id=<ALERT_ID> \
    --confidence_score=<CONFIDENCE_SCORE> \
    --priority=<PRIORITY> \
    --reason=<REASON> \
    --reputation=<REPUTATION> \
    --priority=<PRIORITY> \
    --status=<STATUS> \
    --verdict=<VERDICT> \
    --risk_score=<RISK_SCORE> \
    --disregarded=<DISREGARDED> \
    --severity=<SEVERITY> \
    --comment=<COMMENT> \
    --root_cause=<ROOT_CAUSE> \
    --severity_display=<SEVERITY_DISPLAY>

# pylint: disable=line-too-long
API reference:
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacyUpdateAlert
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Priority
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Reason
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Reputation
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Priority
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Status
  https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/Noun#Verdict
"""
# pylint: enable=line-too-long

import argparse
import json
from typing import Any, Literal, Mapping

from common import chronicle_auth
from common import project_id
from common import project_instance
from common import regions

from google.auth.transport import requests

CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]

PRIORITY_ENUM = (
    "PRIORITY_UNSPECIFIED",
    "PRIORITY_INFO",
    "PRIORITY_LOW",
    "PRIORITY_MEDIUM",
    "PRIORITY_HIGH",
    "PRIORITY_CRITICAL",
)
REASON_ENUM = (
    "REASON_UNSPECIFIED",
    "REASON_NOT_MALICIOUS",
    "REASON_MALICIOUS",
    "REASON_MAINTENANCE",
)
REPUTATION_ENUM = (
    "REPUTATION_UNSPECIFIED",
    "USEFUL",
    "NOT_USEFUL",
)
STATUS_ENUM = (
    "STATUS_UNSPECIFIED",
    "NEW",
    "REVIEWED",
    "CLOSED",
    "OPEN",
)
VERDICT_ENUM = (
    "VERDICT_UNSPECIFIED",
    "TRUE_POSITIVE",
    "FALSE_POSITIVE",
)


def get_update_parser():
  """Returns an argparse.ArgumentParser for the update_alert command."""
  parser = argparse.ArgumentParser()
  chronicle_auth.add_argument_credentials_file(parser)
  project_instance.add_argument_project_instance(parser)
  project_id.add_argument_project_id(parser)
  regions.add_argument_region(parser)
  parser.add_argument(
      "--comment",
      type=str,
      required=False,
      default=None,
      help="Analyst comment.",
  )
  parser.add_argument(
      "--confidence_score",
      type=int,
      required=False,
      default=None,
      help="confidence score [1-100] of the finding",
  )
  parser.add_argument(
      "--disregarded",
      type=bool,
      required=False,
      default=None,
      help="Analyst disregard (or un-disregard) the event",
  )
  parser.add_argument(
      "--priority",
      choices=PRIORITY_ENUM,
      required=False,
      default=None,
      help="alert priority.",
  )
  parser.add_argument(
      "--reason",
      choices=REASON_ENUM,
      required=False,
      default=None,
      help="reason for closing an Alert",
  )
  parser.add_argument(
      "--reputation",
      choices=REPUTATION_ENUM,
      required=False,
      default=None,
      help="A categorization of the finding as useful or not useful",
  )
  parser.add_argument(
      "--risk_score",
      type=int,
      required=False,
      default=None,
      help="risk score [0-100] of the finding",
  )
  parser.add_argument(
      "--root_cause",
      type=str,
      required=False,
      default=None,
      help="Alert root cause.",
  )
  parser.add_argument(
      "--status",
      choices=STATUS_ENUM,
      required=False,
      default=None,
      help="alert status",
  )
  parser.add_argument(
      "--verdict",
      choices=VERDICT_ENUM,
      required=False,
      default=None,
      help="a verdict on whether the finding reflects a security incident",
  )
  parser.add_argument(
      "--severity",
      type=int,
      required=False,
      default=None,
      help="severity score [0-100] of the finding",
  )
  return parser


def check_args(
    parser: argparse.ArgumentParser,
    args_to_check: argparse.Namespace):
  """Checks if at least one of the required arguments is provided.

  Args:
    parser: instance of argparse.ArgumentParser (to raise error if needed).
    args_to_check: instance of argparse.Namespace with the arguments to check.
  """
  if not any(
      [
          args_to_check.comment or args_to_check.comment == "",  # pylint: disable=g-explicit-bool-comparison
          args_to_check.disregarded,
          args_to_check.priority,
          args_to_check.reason,
          args_to_check.reputation,
          args_to_check.risk_score or args_to_check.risk_score == 0,
          args_to_check.root_cause or args_to_check.root_cause == "",  # pylint: disable=g-explicit-bool-comparison
          args_to_check.severity or args_to_check.severity == 0,
          args_to_check.status,
          args_to_check.verdict,
      ]
  ):
    parser.error("At least one of the arguments "
                 "--comment, "
                 "--disregarded, "
                 "--priority, "
                 "--reason, "
                 "--reputation, "
                 "--risk_score, "
                 "--root_cause, "
                 "--severity, "
                 "--status, "
                 "or --verdict "
                 "is required.")


def update_alert(
    http_session: requests.AuthorizedSession,
    proj_id: str,
    proj_instance: str,
    proj_region: str,
    alert_id: str,
    confidence_score: int | None = None,
    reason: str | None = None,
    reputation: str | None = None,
    priority: str | None = None,
    status: str | None = None,
    verdict: str | None = None,
    risk_score: int | None = None,
    disregarded: bool | None = None,
    severity: int | None = None,
    comment: str | Literal[""] | None = None,
    root_cause: str | Literal[""] | None = None,
    ) -> Mapping[str, Any]:
  """Updates an Alert.

  Args:
    http_session: Authorized session for HTTP requests.
    proj_id: GCP project id or number to which the target instance belongs.
    proj_instance: Customer ID (uuid with dashes) for the Chronicle instance.
    proj_region: Region in which the target project is located.
    alert_id: Identifier for the alert.
    confidence_score: Confidence score [0-100] of the finding.
    reason: Reason for closing an Alert.
    reputation: A categorization of the finding as useful or not useful.
    priority: Alert priority.
    status: Status of the alert.
    verdict: Verdict of the alert.
    risk_score: Risk score [0-100] of the finding.
    disregarded: Analyst disregard (or un-disregard) the event.
    severity: Severity score [0-100] of the finding.
    comment: Analyst comment in free text. Empty string is a valid value.
    root_cause: Alert root cause in free text. Empty string unsets the value.

  Returns:
    Dictionary representation of the Alert

  Raises:
    requests.exceptions.HTTPError: HTTP request resulted in an error
      (response.status_code >= 400).
  """
  base_url_with_region = regions.url_always_prepend_region(
      CHRONICLE_API_BASE_URL,
      proj_region
  )
  # pylint: disable-next=line-too-long
  parent = f"projects/{proj_id}/locations/{proj_region}/instances/{proj_instance}"
  url = f"{base_url_with_region}/v1alpha/{parent}/legacy:legacyUpdateAlert/"

  feedback = {}
  if confidence_score or confidence_score == 0:
    feedback["confidence_score"] = confidence_score
  if reason:
    feedback["reason"] = reason
  if reputation:
    feedback["reputation"] = reputation
  if priority:
    feedback["priority"] = priority
  if status:
    feedback["status"] = status
  if verdict:
    feedback["verdict"] = verdict
  if risk_score or risk_score == 0:
    feedback["risk_score"] = risk_score
  if disregarded:
    feedback["disregarded"] = disregarded
  if severity or severity == 0:
    feedback["severity"] = severity
  if comment or comment == "":  # pylint: disable=g-explicit-bool-comparison
    feedback["comment"] = comment
  if root_cause or root_cause == "":  # pylint: disable=g-explicit-bool-comparison
    feedback["root_cause"] = root_cause

  payload = {
      "alert_id": alert_id,
      "feedback": feedback,
  }

  response = http_session.request("POST", url, json=payload)

  # Expected server response is described in:
  # https://cloud.google.com/chronicle/docs/reference/rest/v1alpha/projects.locations.instances.legacy/legacyUpdateAlert
  if response.status_code >= 400:
    print(response.text)
  response.raise_for_status()
  return response.json()


if __name__ == "__main__":
  main_parser = get_update_parser()
  main_parser.add_argument(
      "--alert_id", type=str, required=True,
      help="identifier for the alert"
  )
  args = main_parser.parse_args()

  # Check if at least one of the specific arguments is provided
  check_args(main_parser, args)

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  a_list = update_alert(
      auth_session,
      args.project_id,
      args.project_instance,
      args.region,
      args.alert_id,
      args.confidence_score,
      args.reason,
      args.reputation,
      args.priority,
      args.status,
      args.verdict,
      args.risk_score,
      args.disregarded,
      args.severity,
      args.comment,
      args.root_cause,
  )
  print(json.dumps(a_list, indent=2))
