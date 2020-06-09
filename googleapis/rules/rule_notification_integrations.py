#!/usr/bin/env python3
# Copyright 2020 Google Inc.
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

# Lint as: python3
"""Examples of integrations with other products.

Upon receiving rule notifications from stream_rule_notifications, the customers
will likely want to integrate with other platforms.
Examples of such integrations are below.


These examples are for python3.
"""

import collections
import json
import logging
import requests

_LOGGER_ = logging.getLogger(__name__)

# The slack integration is disabled when WEBHOOK_URL is None.
# To try the slack webhook integration, populate WEBHOOK_URL with a string, e.g.
# WEBHOOK_URL = "https://hooks.slack.com/services/yourWebhookHere"
WEBHOOK_URL = None

# Notification batches might have lots of notifications. We want to avoid
# dumping lots of UDM text into the terminal output or the slack chat room.
# For all notification batches, we'll summarize the notification batch (e.g. how
# many notifications came from which rule/jobs).
# However, for notification batches with more notifications than
# MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL,
# we'll omit reporting on each notification individually.
# Increase this if you're fine with noisier outputs.
MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL = 100

# See https://api.slack.com/changelog/2018-04-truncating-really-long-messages
# Long messages will be truncated after 40k characters (resulting in data being omitted).
# Additionally, long messages will be split into multiple messages, which
# will interrupt formatting blocks such as triple backticks, ```.
# To avoid both of the above, we can send multiple smaller messages.
# Each message posted will contain at most this many rule notifications.
NOTIFICATIONS_PER_WEBHOOK_MESSAGE = 3


def slack_webhook(continuation_time, notifications):
  """Process one notification batch from stream_rule_notifications.

  Forms a textual report to summarize notifications, logs it, then
  sends the report to a slack webhook.

  Args:
    continuation_time: pass in notification_batch["continuationTime"], which is
      a string containing a time in rfc3339 format, that we will log
    notifications: pass in notification_batch["notifications"], which is a list
      of dictionaries containing rule notifications

  Returns:
    None
  """

  batch_size = len(notifications)

  report_lines = []
  report_lines.append(
      "Got stream response with continuationTime {}, containing {} notifications."
      .format(continuation_time, batch_size))

  # Aggregate by each (RuleID/Operation), and list the count of
  # associated notifications. Recall that the server's notifications
  # ARE NOT AGGREGATED, and are NOT SORTED in any particular grouping/order.
  # This aggregation is done entirely within this python client code.
  report_lines.append("Summary of notifications:")
  # notif_metadatas is a list of the metadata (i.e., RuleID and operation name)
  # from all the notifications.
  notif_metadatas = [
      tuple((notif["ruleId"], notif["operation"])) for notif in notifications
  ]
  for notif_metadata, count in collections.Counter(notif_metadatas).items():
    report_lines.append(
        "\t{} notifications from Rule `{}`, Operation `{}`".format(
            count, notif_metadata[0], notif_metadata[1]))

  if batch_size > MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL:
    # Avoid flooding our output channels.
    report_lines.append(
        "Omitting UDM events because more than {} total notifications were received."
        .format(MAX_BATCH_SIZE_TO_REPORT_IN_DETAIL))
    report_lines.append("To get results for an operation listed above, "
                        "call list_results and pass in that operation.")
    report_lines.append("")
    report_string = "\n".join(report_lines)

    _LOGGER_.info(report_string)
    if WEBHOOK_URL:
      requests.post(WEBHOOK_URL, json={"text": report_string})
  else:
    # Output each notification's metadata (Rule and Operation IDs), and its UDM event.
    report_lines.append("UDM events from notifications are listed below:")
    for idx, notif in enumerate(notifications):
      report_lines.append("{}) from Rule `{}`, Operation `{}`".format(
          idx, notif["ruleId"], notif["operation"]))
      report_lines.append("```{}```".format(
          json.dumps(notif["result"]["match"], indent="\t")))

      if idx % NOTIFICATIONS_PER_WEBHOOK_MESSAGE == 0 or idx == batch_size - 1:
        # Construct a report string, then clear out report_lines so the
        # next iterations can start building an new list.
        report_string = "\n".join(report_lines)
        report_lines.clear()
        report_lines.append("")

        _LOGGER_.info(report_string)
        if WEBHOOK_URL:
          requests.post(WEBHOOK_URL, json={"text": report_string})
