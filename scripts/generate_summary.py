#!/usr/bin/env python3
"""Generate a professional Markdown workflow summary."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def _status_emoji(status: str) -> str:
    normalized = status.lower()
    if normalized in {"success", "succeeded"}:
        return "✅"
    if normalized in {"failure", "failed"}:
        return "❌"
    if normalized in {"cancelled", "canceled"}:
        return "⚠️"
    return "ℹ️"


def _format_duration(seconds: float | None) -> str:
    if seconds is None:
        return "N/A"
    total = int(seconds)
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def build_summary(data: dict) -> str:
    status = data.get("status", "unknown")
    emoji = _status_emoji(status)
    records = data.get("records_processed", "")
    records_display = records if records not in ("", None) else "N/A"
    warnings = data.get("warnings", "").strip() or "None"
    error_message = data.get("error_message", "").strip() or "None"
    action_required = data.get("action_required", "").strip() or "No action required."

    start = _parse_iso(data.get("start_time", ""))
    end = _parse_iso(data.get("end_time", ""))
    duration = data.get("duration_seconds")
    if duration is None and start and end:
        duration = (end - start).total_seconds()

    run_url = data.get("run_url", "")
    artifact_url = data.get("artifact_url", "")

    lines = [
        f"# {emoji} Workflow Job Summary",
        "",
        f"**Overall status:** {status.upper()}",
        "",
        "## Run Details",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Repository | `{data.get('repository', 'N/A')}` |",
        f"| Workflow | `{data.get('workflow', 'N/A')}` |",
        f"| Trigger | `{data.get('trigger', 'N/A')}` |",
        f"| Branch | `{data.get('branch', 'N/A')}` |",
        f"| Commit SHA | `{data.get('commit_sha', 'N/A')[:12]}` |",
        f"| Start Time (UTC) | `{data.get('start_time', 'N/A')}` |",
        f"| End Time (UTC) | `{data.get('end_time', 'N/A')}` |",
        f"| Duration | `{_format_duration(duration)}` |",
        f"| Records Processed | `{records_display}` |",
        "",
        "## Health",
        "",
        f"### ⚠️ Warnings",
        warnings,
        "",
        f"### 🧨 Error",
        error_message,
        "",
        f"### 🛠️ Next Recommended Action",
        action_required,
        "",
        "## Links",
        "",
    ]

    if run_url:
        lines.append(f"- [View workflow run]({run_url})")
    if artifact_url:
        lines.append(f"- [Download job summary artifact]({artifact_url})")
    if data.get("failed_step"):
        lines.append(f"- **Failed step:** `{data['failed_step']}`")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build workflow summary markdown.")
    parser.add_argument("--input-json", type=Path, required=True, help="JSON file with summary fields")
    parser.add_argument("--output-file", type=Path, required=True, help="Write markdown summary here")
    parser.add_argument("--step-summary-file", type=Path, default=None, help="GITHUB_STEP_SUMMARY file path")
    args = parser.parse_args()

    data = json.loads(args.input_json.read_text(encoding="utf-8"))
    markdown = build_summary(data)

    args.output_file.parent.mkdir(parents=True, exist_ok=True)
    args.output_file.write_text(markdown, encoding="utf-8")

    if args.step_summary_file:
        args.step_summary_file.write_text(markdown, encoding="utf-8")

    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
