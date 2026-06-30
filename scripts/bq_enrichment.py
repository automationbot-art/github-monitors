#!/usr/bin/env python3
"""PKT timezone conversion, cron helpers, and Looker dashboard enrichment fields."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

PKT = ZoneInfo("Asia/Karachi")
PKT_LABEL = "PKT"
LATE_RUN_THRESHOLD_MINUTES = 15


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def to_pkt(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(PKT)


def pkt_date(dt: datetime | None) -> str | None:
    local = to_pkt(dt)
    return local.date().isoformat() if local else None


def pkt_datetime_value(dt: datetime | None) -> str | None:
    """BigQuery DATETIME string (wall clock in PKT, no offset)."""
    local = to_pkt(dt)
    if not local:
        return None
    return local.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")


def pkt_label(dt: datetime | None) -> str | None:
    local = to_pkt(dt)
    if not local:
        return None
    return local.strftime("%d %b %Y, %I:%M %p PKT")


def day_of_week_pkt(dt: datetime | None) -> str | None:
    local = to_pkt(dt)
    return local.strftime("%A") if local else None


def hour_of_day_pkt(dt: datetime | None) -> int | None:
    local = to_pkt(dt)
    return local.hour if local else None


def parse_cron_parts(cron: str | None) -> tuple[int, int] | None:
    """Parse minute and hour from a standard 5-field cron (GitHub Actions UTC)."""
    if not cron:
        return None
    parts = cron.strip().split()
    if len(parts) < 2:
        return None
    minute, hour = parts[0], parts[1]
    if not (minute.isdigit() and hour.isdigit()):
        return None
    return int(minute), int(hour)


def cron_description_pkt(cron: str | None) -> str | None:
    parsed = parse_cron_parts(cron)
    if not parsed:
        return None
    minute, hour_utc = parsed
    # Build expected UTC time on arbitrary day, convert to PKT for label.
    sample = datetime(2026, 1, 1, hour_utc, minute, tzinfo=timezone.utc)
    local = sample.astimezone(PKT)
    time_label = local.strftime("%I:%M %p").lstrip("0")
    return f"Daily at {time_label} {PKT_LABEL}"


def expected_run_utc(cron: str | None, reference: datetime) -> datetime | None:
    parsed = parse_cron_parts(cron)
    if not parsed:
        return None
    minute, hour_utc = parsed
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)
    return datetime(
        reference.year,
        reference.month,
        reference.day,
        hour_utc,
        minute,
        tzinfo=timezone.utc,
    )


def compute_delay(started: datetime | None, expected: datetime | None) -> tuple[bool, int | None]:
    if not started or not expected:
        return False, None
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    if expected.tzinfo is None:
        expected = expected.replace(tzinfo=timezone.utc)
    delta = started - expected
    minutes = int(delta.total_seconds() // 60)
    if minutes <= LATE_RUN_THRESHOLD_MINUTES:
        return False, max(minutes, 0)
    return True, minutes


def severity(outcome: str, has_warnings: bool) -> str:
    outcome = (outcome or "").lower()
    if outcome == "failure":
        return "error"
    if outcome == "success" and has_warnings:
        return "warning"
    if outcome == "success":
        return "success"
    if outcome in {"cancelled", "canceled"}:
        return "info"
    return "info"


def trigger_metadata(trigger_type: str, schedule_status_input: str = "") -> dict:
    """Classify how the workflow was triggered for Looker dashboards."""
    trigger = (trigger_type or "").strip().lower()
    schedule_input = (schedule_status_input or "").strip().lower()

    if trigger == "workflow_dispatch":
        return {
            "run_mode": "Manual",
            "trigger_type_label": "Manual Run",
            "is_manual_run": True,
            "is_scheduled_run": False,
            "schedule_status": "Disabled (manual only)"
            if schedule_input in {"disabled", "manual-only", "manual_only", "commented"}
            else "Manual trigger",
        }

    if trigger == "schedule":
        return {
            "run_mode": "Scheduled",
            "trigger_type_label": "Scheduled Cron",
            "is_manual_run": False,
            "is_scheduled_run": True,
            "schedule_status": "Active",
        }

    return {
        "run_mode": "Other",
        "trigger_type_label": trigger.replace("_", " ").title() if trigger else "Unknown",
        "is_manual_run": False,
        "is_scheduled_run": False,
        "schedule_status": schedule_input or "Not configured",
    }


def operator_instruction(
    outcome: str,
    has_warnings: bool,
    is_late_run: bool,
    action_required: str | None,
    error_message: str | None,
    records_processed: int | None,
    is_manual_run: bool = False,
) -> str:
    outcome = (outcome or "").lower()
    action_required = (action_required or "").strip()
    error_message = (error_message or "").strip()

    if outcome == "failure":
        if action_required and action_required.lower() != "no action required.":
            return action_required
        if error_message and error_message.lower() != "none":
            return f"Fix failure: {error_message[:200]}"
        return "Open the workflow run, review the failed step log, fix the root cause, and re-run."

    if outcome == "success" and has_warnings:
        return "Job completed but warnings were logged — review warnings and confirm data quality in Looker."

    if is_late_run:
        return "Run started late — check GitHub Actions queue, runner availability, or upstream delays."

    if outcome == "success" and records_processed == 0:
        return "Run succeeded but processed 0 records — verify source data and script filters."

    if outcome == "success":
        if is_manual_run:
            return "No action needed — manual run completed successfully."
        return "No action needed — monitor the next scheduled run."

    if outcome in {"cancelled", "canceled"}:
        return "Run was cancelled — re-trigger manually if the job still needs to execute."

    return "Review the workflow run details in GitHub Actions."


def needs_attention(
    outcome: str,
    has_warnings: bool,
    is_late_run: bool,
    records_processed: int | None,
) -> bool:
    outcome = (outcome or "").lower()
    if outcome == "failure":
        return True
    if has_warnings:
        return True
    if is_late_run:
        return True
    if outcome == "success" and records_processed == 0:
        return True
    return False


def build_remarks(
    outcome: str,
    warnings: str,
    error_message: str,
    is_manual_run: bool = False,
) -> str:
    warnings = (warnings or "").strip()
    error_message = (error_message or "").strip()
    outcome = (outcome or "unknown").lower()
    prefix = "Manual run — " if is_manual_run else ""

    if outcome == "success":
        if warnings and warnings.lower() not in {"none", "n/a"}:
            return f"{prefix}Successful with warnings: {warnings}"
        return f"{prefix}Successful — completed without errors"

    if outcome == "failure":
        if error_message and error_message.lower() != "none":
            return f"{prefix}Failed — {error_message}"
        return f"{prefix}Failed — see workflow logs for details"

    if outcome == "cancelled":
        return f"{prefix}Cancelled — workflow run was cancelled"

    if outcome == "skipped":
        return f"{prefix}Skipped — job did not execute"

    return f"{prefix}Completed with outcome: {outcome}"


def dashboard_status_label(outcome: str, execution_status: str, run_mode: str = "Scheduled") -> str:
    """Looker-friendly status: Ran / Pending paired with outcome and run mode."""
    execution_status = execution_status or "Ran"
    outcome = (outcome or "unknown").lower()
    mode = run_mode or "Scheduled"

    if execution_status == "Pending":
        return "Pending"

    prefix = "Manual — " if mode == "Manual" else "Ran — "

    if outcome == "success":
        return f"{prefix}Success"
    if outcome == "failure":
        return f"{prefix}Failed"
    if outcome in {"cancelled", "canceled"}:
        return f"{prefix}Cancelled"
    return f"{prefix}{outcome.title()}"
