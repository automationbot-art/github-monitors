#!/usr/bin/env python3
"""Build JSON input for generate_summary.py from environment variables."""

from __future__ import annotations

import json
import os


def main() -> None:
    payload = {
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "workflow": os.environ.get("GITHUB_WORKFLOW", ""),
        "trigger": os.environ.get("GITHUB_EVENT_NAME", ""),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "start_time": os.environ.get("START_TIME", ""),
        "end_time": os.environ.get("END_TIME", ""),
        "status": os.environ.get("INPUT_STATUS", "unknown"),
        "records_processed": os.environ.get("INPUT_RECORDS", ""),
        "warnings": os.environ.get("INPUT_WARNINGS", ""),
        "error_message": os.environ.get("ERROR_MESSAGE", ""),
        "action_required": os.environ.get("ACTION_REQUIRED", ""),
        "run_url": os.environ.get("RUN_URL", ""),
        "artifact_url": os.environ.get("ARTIFACT_URL", ""),
        "failed_step": os.environ.get("FAILED_STEP", ""),
    }
    print(json.dumps(payload))


if __name__ == "__main__":
    main()
