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
"""Chronicle Search API commands."""

import click
from common import chronicle_auth

from search.v1alpha import asset_events_find
from search.v1alpha import raw_logs_find
from search.v1alpha import search_query_get
from search.v1alpha import udm_events_find

SCOPES = [
    "https://www.googleapis.com/auth/cloud-platform",
]


@click.group()
def search():
  """Search API commands."""
  pass


@search.command("find-asset-events")
@click.option(
    "--asset-indicator",
    required=True,
    help="The asset indicator to search for.",
)
@click.option(
    "--start-time",
    required=True,
    help="RFC3339 formatted timestamp for the start time.",
)
@click.option(
    "--end-time",
    required=True,
    help="RFC3339 formatted timestamp for the end time.",
)
@click.option(
    "--page-size",
    type=int,
    help="Optional maximum number of results to return.",
)
@click.option(
    "--page-token",
    help="Optional page token from a previous response.",
)
@click.pass_context
def find_asset_events_cmd(ctx, asset_indicator, start_time, end_time, page_size,
                          page_token):
  """Find asset events within a time range."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  asset_events_find.find_asset_events(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      asset_indicator,
      start_time,
      end_time,
      page_size,
      page_token,
  )


@search.command("find-raw-logs")
@click.option(
    "--query",
    required=True,
    help="Search parameters that expand or restrict the search.",
)
@click.option(
    "--batch-tokens",
    multiple=True,
    help="Optional list of tokens that should be downloaded.",
)
@click.option(
    "--log-ids",
    multiple=True,
    help="Optional list of raw log ids that should be downloaded.",
)
@click.option(
    "--regex-search",
    is_flag=True,
    help="Treat query as regex.",
)
@click.option(
    "--case-sensitive",
    is_flag=True,
    help="Make search case-sensitive.",
)
@click.option(
    "--max-response-size",
    type=int,
    help="Optional maximum response size in bytes.",
)
@click.pass_context
def find_raw_logs_cmd(ctx, query, batch_tokens, log_ids, regex_search,
                      case_sensitive, max_response_size):
  """Find raw logs based on search criteria."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  raw_logs_find.find_raw_logs(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      query,
      list(batch_tokens) if batch_tokens else None,
      list(log_ids) if log_ids else None,
      regex_search,
      case_sensitive,
      max_response_size,
  )


@search.command("find-udm-events")
@click.option(
    "--tokens",
    multiple=True,
    help=
    "Optional list of tokens, with each token referring to a group of "
    "UDM/Entity events.",
)
@click.option(
    "--event-ids",
    multiple=True,
    help="Optional list of UDM/Entity event ids that should be returned.",
)
@click.option(
    "--return-unenriched-data",
    is_flag=True,
    help="Return unenriched data.",
)
@click.option(
    "--return-all-events-for-log",
    is_flag=True,
    help="Return all events generated from the ingested log.",
)
@click.pass_context
def find_udm_events_cmd(ctx, tokens, event_ids, return_unenriched_data,
                        return_all_events_for_log):
  """Find UDM events based on tokens or event IDs."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  udm_events_find.find_udm_events(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      list(tokens) if tokens else None,
      list(event_ids) if event_ids else None,
      return_unenriched_data,
      return_all_events_for_log,
  )


@search.command("get-search-query")
@click.option(
    "--user-id",
    required=True,
    help="ID of the user who owns the search query.",
)
@click.option(
    "--query-id",
    required=True,
    help="ID of the search query to retrieve.",
)
@click.pass_context
def get_search_query_cmd(ctx, user_id, query_id):
  """Get a search query by ID."""
  auth_session = chronicle_auth.initialize_http_session(
      ctx.obj["credentials_file"],
      SCOPES,
  )
  search_query_get.get_search_query(
      auth_session,
      ctx.obj["project_id"],
      ctx.obj["project_instance"],
      ctx.obj["region"],
      user_id,
      query_id,
  )
