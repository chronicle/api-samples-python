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
r"""Executable and reusable sample for bulk updating alerts.

The file provided to the --alert_ids_file parameter should have one alert 
 ID per line like so:
```
de_ad9d2771-a567-49ee-6452-1b2db13c1d33
de_3c2e2556-aba1-a253-7518-b4ddb666cc32
```
Usage:
  python -m alerts.v1alpha.bulk_update_alerts \
    --project_id=<PROJECT_ID>   \
    --project_instance=<PROJECT_INSTANCE> \
    --alert_ids_file=<PATH_TO_FILE> \
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

import json

from common import chronicle_auth

from . import update_alert


CHRONICLE_API_BASE_URL = "https://chronicle.googleapis.com"
SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]
DEFAULT_FEEDBACK = {
    "comment": "automated cleanup",
    "reason": "REASON_MAINTENANCE",
    "reputation": "REPUTATION_UNSPECIFIED",
    "root_cause": "Other",
    "status": "CLOSED",
    "verdict": "VERDICT_UNSPECIFIED",
}


if __name__ == "__main__":
  parser = update_alert.get_update_parser()
  parser.add_argument(
      "--alert_ids_file", type=str, required=True,
      help="File with one alert ID per line."
  )
  parser.set_defaults(
      comment=DEFAULT_FEEDBACK["comment"],
      reason=DEFAULT_FEEDBACK["reason"],
      reputation=DEFAULT_FEEDBACK["reputation"],
      root_cause=DEFAULT_FEEDBACK["root_cause"],
      status=DEFAULT_FEEDBACK["status"],
      verdict=DEFAULT_FEEDBACK["verdict"],
  )
  args = parser.parse_args()

  # raise error if required args are not present
  update_alert.check_args(parser, args)

  auth_session = chronicle_auth.initialize_http_session(
      args.credentials_file,
      SCOPES,
  )
  with open(args.alert_ids_file) as fh:
    for alert_id in fh:
      a_list = update_alert.update_alert(
          auth_session,
          args.project_id,
          args.project_instance,
          args.region,
          alert_id.strip(),
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
