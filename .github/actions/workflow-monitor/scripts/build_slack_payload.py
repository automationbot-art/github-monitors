#!/usr/bin/env python3
"""Build Slack incoming-webhook payload for workflow failures."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    repository = os.environ.get("REPOSITORY", "unknown")
    workflow = os.environ.get("WORKFLOW", "unknown")
    failed_step = os.environ.get("FAILED_STEP") or "Unknown step"
    error_message = os.environ.get("ERROR_MESSAGE") or "No error message captured."
    action_required = os.environ.get("ACTION_REQUIRED") or "Review the workflow run log."
    run_url = os.environ.get("RUN_URL", "")
    artifact_url = os.environ.get("ARTIFACT_URL", "")

    payload = {
        "text": "🚨 GitHub Workflow Failed",
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": "🚨 GitHub Workflow Failed"},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Repository:*\n`{repository}`"},
                    {"type": "mrkdwn", "text": f"*Workflow:*\n`{workflow}`"},
                ],
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Failed Step:*\n`{failed_step}`"},
                    {"type": "mrkdwn", "text": f"*Run URL:*\n<{run_url}|Open workflow run>"},
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Reason:*\n```{error_message[:2900]}```",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Action Required:*\n{action_required}",
                },
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Job Summary:*\n<{artifact_url}|workflow-summary artifact>",
                },
            },
        ],
    }

    output = Path(os.environ["PAYLOAD_FILE"])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload), encoding="utf-8")


if __name__ == "__main__":
    main()
