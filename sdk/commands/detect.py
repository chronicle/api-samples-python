#!/usr/bin/env python3

# Copyright 2025 Google LLC
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
"""Chronicle Detection API commands."""

import json

import click
from common import chronicle_auth
from detect.v1alpha import batch_update_curated_rule_set_deployments
from detect.v1alpha import bulk_update_alerts
from detect.v1alpha import create_retrohunt
from detect.v1alpha import create_rule
from detect.v1alpha import delete_rule
from detect.v1alpha import enable_rule
from detect.v1alpha import get_alert
from detect.v1alpha import get_detection
from detect.v1alpha import get_retrohunt
from detect.v1alpha import get_rule
from detect.v1alpha import list_detections
from detect.v1alpha import list_errors
from detect.v1alpha import list_rules
from detect.v1alpha import update_alert
from sdk.commands.common import add_common_options

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


@click.group()
def detect():
  """Detection API commands."""
  pass


# Alert Management Commands
@detect.group()
def alerts():
  """Alert management commands."""
  pass


@alerts.command("get")
@add_common_options
@click.option(
    "--alert-id",
    required=True,
    help="Identifier for the alert.",
)
@click.option(
    "--include-detections",
    is_flag=True,
    help="Include non-alerting detections.",
)
def get_alert_cmd(credentials_file, project_id, project_instance, region,
                  alert_id, include_detections):
  """Get an alert by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  alert = get_alert.get_alert(
      auth_session,
      project_id,
      project_instance,
      region,
      alert_id,
      include_detections,
  )
  print(json.dumps(alert, indent=2))


@alerts.command("update")
@add_common_options
@click.option(
    "--alert-id",
    required=True,
    help="Identifier for the alert.",
)
@click.option(
    "--update-mask",
    required=True,
    help="Comma-separated list of fields to update.",
)
@click.option(
    "--json-body",
    required=True,
    help="JSON string containing the update data.",
)
def update_alert_cmd(credentials_file, project_id, project_instance, region,
                     alert_id, update_mask, json_body):
  """Update an alert."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = update_alert.update_alert(
      auth_session,
      project_id,
      project_instance,
      region,
      alert_id,
      update_mask,
      json_body,
  )
  print(json.dumps(result, indent=2))


@alerts.command("bulk-update")
@add_common_options
@click.option(
    "--a_filter",
    required=True,
    help="a_filter to select alerts to update.",
)
@click.option(
    "--update-mask",
    required=True,
    help="Comma-separated list of fields to update.",
)
@click.option(
    "--json-body",
    required=True,
    help="JSON string containing the update data.",
)
def bulk_update_alerts_cmd(credentials_file, project_id, project_instance,
                           region, a_filter, update_mask, json_body):
  """Bulk update alerts matching a filter."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = bulk_update_alerts.bulk_update_alerts(
      auth_session,
      project_id,
      project_instance,
      region,
      a_filter,
      update_mask,
      json_body,
  )
  print(json.dumps(result, indent=2))


# Detection Commands
@detect.group()
def detections():
  """Detection management commands."""
  pass


@detections.command("get")
@add_common_options
@click.option(
    "--detection-id",
    required=True,
    help="Identifier for the detection.",
)
@click.option(
    "--rule-id",
    required=True,
    help="Identifier for the rule that created the detection.",
)
def get_detection_cmd(credentials_file, project_id, project_instance, region,
                      detection_id, rule_id):
  """Get a detection by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  detection = get_detection.get_detection(
      auth_session,
      project_id,
      project_instance,
      region,
      detection_id,
      rule_id,
  )
  print(json.dumps(detection, indent=2))


@detections.command("list")
@add_common_options
@click.option(
    "--a_filter",
    help="a_filter string for the list request.",
)
@click.option(
    "--page-size",
    type=int,
    help="Maximum number of detections to return.",
)
@click.option(
    "--page-token",
    help="Page token from previous response.",
)
def list_detections_cmd(credentials_file, project_id, project_instance, region,
                        a_filter, page_size, page_token):
  """List detections."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = list_detections.list_detections(
      auth_session,
      region,
      project_id,
      project_instance,
      a_filter,
      page_size,
      page_token,
  )
  print(json.dumps(result, indent=2))


# Rule Management Commands
@detect.group()
def rules():
  """Rule management commands."""
  pass


@rules.command("create")
@add_common_options
@click.option(
    "--json-body",
    required=True,
    help="JSON string containing the rule definition.",
)
def create_rule_cmd(credentials_file, project_id, project_instance, region,
                    json_body):
  """Create a new rule."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = create_rule.create_rule(
      auth_session,
      project_id,
      project_instance,
      region,
      json_body,
  )
  print(json.dumps(result, indent=2))


@rules.command("get")
@add_common_options
@click.option(
    "--rule-id",
    required=True,
    help="Identifier for the rule.",
)
def get_rule_cmd(credentials_file, project_id, project_instance, region,
                 rule_id):
  """Get a rule by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = get_rule.get_rule(
      auth_session,
      project_id,
      project_instance,
      region,
      rule_id,
  )
  print(json.dumps(result, indent=2))


@rules.command("delete")
@add_common_options
@click.option(
    "--rule-id",
    required=True,
    help="Identifier for the rule to delete.",
)
def delete_rule_cmd(credentials_file, project_id, project_instance, region,
                    rule_id):
  """Delete a rule."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  delete_rule.delete_rule(
      auth_session,
      project_id,
      project_instance,
      region,
      rule_id,
  )


@rules.command("enable")
@add_common_options
@click.option(
    "--rule-id",
    required=True,
    help="Identifier for the rule to enable.",
)
def enable_rule_cmd(credentials_file, project_id, project_instance, region,
                    rule_id):
  """Enable a rule."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = enable_rule.enable_rule(
      auth_session,
      project_id,
      project_instance,
      region,
      rule_id,
  )
  print(json.dumps(result, indent=2))


@rules.command("list")
@add_common_options
@click.option(
    "--a_filter",
    help="a_filter string for the list request.",
)
@click.option(
    "--page-size",
    type=int,
    help="Maximum number of rules to return.",
)
@click.option(
    "--page-token",
    help="Page token from previous response.",
)
def list_rules_cmd(credentials_file, project_id, project_instance, region,
                   a_filter, page_size, page_token):
  """List rules."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = list_rules.list_rules(
      auth_session,
      project_id,
      project_instance,
      region,
      a_filter,
      page_size,
      page_token,
  )
  print(json.dumps(result, indent=2))


# Retrohunt Commands
@detect.group()
def retrohunts():
  """Retrohunt management commands."""
  pass


@retrohunts.command("create")
@add_common_options
@click.option(
    "--json-body",
    required=True,
    help="JSON string containing the retrohunt configuration.",
)
def create_retrohunt_cmd(credentials_file, project_id, project_instance, region,
                         json_body):
  """Create a new retrohunt."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = create_retrohunt.create_retrohunt(
      auth_session,
      project_id,
      project_instance,
      region,
      json_body,
  )
  print(json.dumps(result, indent=2))


@retrohunts.command("get")
@add_common_options
@click.option(
    "--retrohunt-id",
    required=True,
    help="Identifier for the retrohunt.",
)
def get_retrohunt_cmd(credentials_file, project_id, project_instance, region,
                      retrohunt_id):
  """Get a retrohunt by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = get_retrohunt.get_retrohunt(
      auth_session,
      project_id,
      project_instance,
      region,
      retrohunt_id,
  )
  print(json.dumps(result, indent=2))


# Error Management Commands
@detect.group()
def errors():
  """Error management commands."""
  pass


@errors.command("list")
@add_common_options
@click.option(
    "--a_filter",
    help="a_filter string for the list request.",
)
@click.option(
    "--page-size",
    type=int,
    help="Maximum number of errors to return.",
)
@click.option(
    "--page-token",
    help="Page token from previous response.",
)
def list_errors_cmd(credentials_file, project_id, project_instance, region,
                    a_filter, page_size, page_token):
  """List errors."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  result = list_errors.list_errors(
      auth_session,
      project_id,
      project_instance,
      region,
      a_filter,
      page_size,
      page_token,
  )
  print(json.dumps(result, indent=2))


# Rule Set Deployment Commands
@detect.group()
def rulesets():
  """Rule set deployment commands."""
  pass


@rulesets.command("batch-update")
@add_common_options
@click.option(
    "--json-body",
    required=True,
    help="JSON string containing the rule set deployment updates.",
)
def batch_update_rule_sets_cmd(credentials_file, project_id, project_instance,
                               region, json_body):
  """Batch update rule set deployments."""
  auth_session = chronicle_auth.initialize_http_session(
      credentials_file,
      SCOPES,
  )
  # pylint: disable-next=line-too-long
  result = batch_update_curated_rule_set_deployments.batch_update_curated_rule_set_deployments(
      auth_session,
      project_id,
      project_instance,
      region,
      json_body,
  )
  print(json.dumps(result, indent=2))
