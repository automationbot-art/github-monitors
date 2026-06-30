#!/usr/bin/env python3
"""Build a BigQuery row dict from workflow monitor context."""

from __future__ import annotations

import json
import os
import sys
import uuid
from datetime import datetime, timezone


def _parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _duration_seconds(start: str | None, end: str | None) -> int | None:
    start_dt = _parse_ts(start)
    end_dt = _parse_ts(end)
    if start_dt and end_dt:
        return max(int((end_dt - start_dt).total_seconds()), 0)
    return None


def _to_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _build_remarks(outcome: str, warnings: str, error_message: str) -> str:
    warnings = (warnings or "").strip()
    error_message = (error_message or "").strip()
    outcome = (outcome or "unknown").lower()

    if outcome == "success":
        if warnings and warnings.lower() not in {"none", "n/a"}:
            return f"Successful with warnings: {warnings}"
        return "Successful — completed without errors"

    if outcome == "failure":
        if error_message and error_message.lower() != "none":
            return f"Failed — {error_message}"
        return "Failed — see workflow logs for details"

    if outcome == "cancelled":
        return "Cancelled — workflow run was cancelled"

    if outcome == "skipped":
        return "Skipped — job did not execute"

    return f"Completed with outcome: {outcome}"


def _read_log_excerpt(log_file: str | None, limit: int = 4000) -> str | None:
    if not log_file or not os.path.isfile(log_file):
        return None
    text = open(log_file, encoding="utf-8", errors="replace").read()
    return text[-limit:] if len(text) > limit else text


def build_row() -> dict:
    now = datetime.now(timezone.utc)
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    repo_short = repository.split("/", 1)[-1] if repository else None

    outcome = os.environ.get("INPUT_STATUS", "unknown")
    warnings = os.environ.get("INPUT_WARNINGS", "")
    error_message = os.environ.get("ERROR_MESSAGE", "")
    error_type = os.environ.get("ERROR_TYPE", "")
    start_time = os.environ.get("START_TIME", "")
    end_time = os.environ.get("END_TIME", "")

    start_dt = _parse_ts(start_time) or now
    scheduled_time = _parse_ts(os.environ.get("SCHEDULED_TIME_UTC", "")) or start_dt

    has_warnings = bool(
        warnings
        and warnings.strip().lower() not in {"", "none", "n/a"}
        and outcome.lower() == "success"
    )

    return {
        "event_id": str(uuid.uuid4()),
        "recorded_at": now.isoformat(),
        "run_date": start_dt.date().isoformat(),
        "repository_name": repository,
        "repository_short_name": repo_short,
        "workflow_name": os.environ.get("GITHUB_WORKFLOW", ""),
        "job_name": os.environ.get("GITHUB_JOB", ""),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "trigger_type": os.environ.get("GITHUB_EVENT_NAME", ""),
        "scheduled_cron": os.environ.get("SCHEDULED_CRON", "") or None,
        "scheduled_time_utc": scheduled_time.isoformat(),
        "started_at": start_time or None,
        "ended_at": end_time or None,
        "duration_seconds": _duration_seconds(start_time, end_time),
        "execution_status": "Ran",
        "workflow_outcome": outcome,
        "remarks": _build_remarks(outcome, warnings, error_message),
        "error_message": None if error_message in {"", "None"} else error_message,
        "error_type": error_type or None,
        "failed_step": os.environ.get("FAILED_STEP") or None,
        "action_required": os.environ.get("ACTION_REQUIRED") or None,
        "records_processed": _to_int(os.environ.get("INPUT_RECORDS")),
        "warnings": warnings or None,
        "has_warnings": has_warnings,
        "github_run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "github_run_number": _to_int(os.environ.get("GITHUB_RUN_NUMBER")),
        "github_run_attempt": _to_int(os.environ.get("GITHUB_RUN_ATTEMPT")),
        "run_url": os.environ.get("RUN_URL", ""),
        "artifact_url": os.environ.get("ARTIFACT_URL", ""),
        "log_excerpt": _read_log_excerpt(os.environ.get("INPUT_LOG_FILE")),
        "ingestion_source": "github-actions-workflow-monitor",
    }


def main() -> int:
    row = build_row()
    print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
