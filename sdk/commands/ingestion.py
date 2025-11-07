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
"""Chronicle Ingestion API commands."""

import click
from common import chronicle_auth

from ingestion.v1alpha import event_import
from ingestion.v1alpha import events_batch_get
from ingestion.v1alpha import events_get

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


@click.group()
def ingestion():
  """Ingestion API commands."""
  pass


@ingestion.command("import-events")
@click.option(
    "--json-events",
    required=True,
    help="Events in (serialized) JSON format.",
)
@click.pass_context
def import_events_cmd(ctx, json_events):
  """Import events into Chronicle."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  event_import.import_events(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      json_events,
  )


@ingestion.command("get-event")
@click.option(
    "--event-id",
    required=True,
    help="The ID of the event to retrieve.",
)
@click.pass_context
def get_event_cmd(ctx, event_id):
  """Get event details by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  events_get.get_event(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      event_id,
  )


@ingestion.command("batch-get-events")
@click.option(
    "--event-ids",
    required=True,
    help="JSON string containing a list of event IDs to retrieve.",
)
@click.pass_context
def batch_get_events_cmd(ctx, event_ids):
  """Batch get events by IDs."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  events_batch_get.batch_get_events(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      event_ids,
  )
