#!/usr/bin/env python3
"""Build a BigQuery row dict from workflow monitor context."""

from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone

from bq_enrichment import (
    PKT_LABEL,
    compute_delay,
    cron_description_pkt,
    dashboard_status_label,
    day_of_week_pkt,
    expected_run_utc,
    hour_of_day_pkt,
    needs_attention,
    operator_instruction,
    parse_ts,
    pkt_date,
    pkt_datetime_value,
    pkt_label,
    severity,
)


def _duration_seconds(start: str | None, end: str | None) -> int | None:
    start_dt = parse_ts(start)
    end_dt = parse_ts(end)
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
    action_required = os.environ.get("ACTION_REQUIRED", "")
    start_time = os.environ.get("START_TIME", "")
    end_time = os.environ.get("END_TIME", "")
    scheduled_cron = os.environ.get("SCHEDULED_CRON", "") or None
    trigger_type = os.environ.get("GITHUB_EVENT_NAME", "")

    start_dt = parse_ts(start_time) or now
    end_dt = parse_ts(end_time)
    scheduled_time = parse_ts(os.environ.get("SCHEDULED_TIME_UTC", "")) or start_dt
    records_processed = _to_int(os.environ.get("INPUT_RECORDS"))

    has_warnings = bool(
        warnings
        and warnings.strip().lower() not in {"", "none", "n/a"}
        and outcome.lower() == "success"
    )

    expected_utc = expected_run_utc(scheduled_cron, start_dt) if trigger_type == "schedule" else None
    is_late_run, delay_minutes = compute_delay(start_dt, expected_utc)
    execution_status = "Ran"
    sev = severity(outcome, has_warnings)
    instruction = operator_instruction(
        outcome, has_warnings, is_late_run, action_required, error_message, records_processed
    )
    attention = needs_attention(outcome, has_warnings, is_late_run, records_processed)

    return {
        "event_id": str(uuid.uuid4()),
        "recorded_at": now.isoformat(),
        "run_date": start_dt.date().isoformat(),
        "run_date_pkt": pkt_date(start_dt),
        "timezone": "Asia/Karachi",
        "timezone_label": PKT_LABEL,
        "repository_name": repository,
        "repository_short_name": repo_short,
        "workflow_name": os.environ.get("GITHUB_WORKFLOW", ""),
        "job_name": os.environ.get("GITHUB_JOB", ""),
        "branch": os.environ.get("GITHUB_REF_NAME", ""),
        "commit_sha": os.environ.get("GITHUB_SHA", ""),
        "trigger_type": trigger_type,
        "scheduled_cron": scheduled_cron,
        "cron_description_pkt": cron_description_pkt(scheduled_cron),
        "scheduled_time_utc": scheduled_time.isoformat(),
        "expected_run_time_utc": expected_utc.isoformat() if expected_utc else None,
        "scheduled_time_pkt": pkt_datetime_value(scheduled_time),
        "scheduled_time_pkt_label": pkt_label(scheduled_time),
        "started_at": start_time or None,
        "started_at_pkt": pkt_datetime_value(start_dt),
        "ended_at": end_time or None,
        "ended_at_pkt": pkt_datetime_value(end_dt),
        "day_of_week_pkt": day_of_week_pkt(start_dt),
        "hour_of_day_pkt": hour_of_day_pkt(start_dt),
        "duration_seconds": _duration_seconds(start_time, end_time),
        "is_late_run": is_late_run,
        "delay_minutes": delay_minutes,
        "execution_status": execution_status,
        "dashboard_status": dashboard_status_label(outcome, execution_status),
        "workflow_outcome": outcome,
        "remarks": _build_remarks(outcome, warnings, error_message),
        "error_message": None if error_message in {"", "None"} else error_message,
        "error_type": error_type or None,
        "failed_step": os.environ.get("FAILED_STEP") or None,
        "action_required": action_required or None,
        "operator_instruction": instruction,
        "severity": sev,
        "needs_attention": attention,
        "records_processed": records_processed,
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
