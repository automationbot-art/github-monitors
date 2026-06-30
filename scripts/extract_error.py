#!/usr/bin/env python3
"""Extract actionable error messages from workflow logs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Ordered patterns: first match wins for the primary error line.
ERROR_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("python_exception", re.compile(r"^(\w+(?:Error|Exception)):\s*(.+)$", re.MULTILINE)),
    ("missing_env", re.compile(r"(?:KeyError|EnvironmentError|.*Missing.*env).*['\"]([A-Z0-9_]+)['\"]", re.IGNORECASE)),
    ("auth_failure", re.compile(r"(?i)(authentication failed|invalid credentials|401 unauthorized|403 forbidden|permission denied)")),
    ("timeout", re.compile(r"(?i)(timeout|timed out|deadline exceeded|context deadline exceeded)")),
    ("bigquery", re.compile(r"(?i)(bigquery error|google\.api_core\.exceptions\.\w+|BadRequest:.*bigquery)")),
    ("api_failure", re.compile(r"(?i)(httpx\.|requests\.|HTTPError|ConnectionError|APIError|status code [45]\d{2})")),
    ("shell_exit", re.compile(r"Process completed with exit code (\d+)")),
]

RECOMMENDED_ACTIONS: dict[str, str] = {
    "python_exception": "Review the traceback in the run log, fix the failing code path, and re-run the workflow.",
    "missing_env": "Add the missing secret or repository variable, then re-run the workflow.",
    "auth_failure": "Rotate or verify API tokens, service account keys, and GitHub secrets; confirm scopes.",
    "timeout": "Increase the job timeout, optimize long-running queries, or add retries for flaky dependencies.",
    "bigquery": "Validate the SQL, table permissions, billing/project ID, and service account access.",
    "api_failure": "Check upstream API status, rate limits, network egress, and request payloads.",
    "shell_exit": "Inspect the step log above the exit code for the root cause, then fix and re-run.",
    "unknown": "Open the workflow run URL, review the failed step log, and apply the fix for the reported error.",
}


def _read_log(log_path: Path | None, stdin_text: str) -> str:
    if log_path and log_path.exists():
        return log_path.read_text(encoding="utf-8", errors="replace")
    return stdin_text


def _extract_traceback(text: str) -> str | None:
    lines = text.splitlines()
    traceback_start = None
    for idx, line in enumerate(lines):
        if line.strip().startswith("Traceback (most recent call last):"):
            traceback_start = idx
    if traceback_start is None:
        return None
    tail = lines[traceback_start:]
    # Keep last exception line plus up to 12 traceback lines for context.
    return "\n".join(tail[-14:])


def _find_failed_step_hint(text: str) -> str | None:
    match = re.search(r"##\[error\](.+)", text)
    return match.group(1).strip() if match else None


def extract_error(text: str, failed_step: str = "") -> dict[str, str]:
    text = text.strip()
    error_type = "unknown"
    message = "Workflow failed without a captured log message. Open the run log for details."
    action = RECOMMENDED_ACTIONS["unknown"]

    traceback = _extract_traceback(text)
    if traceback:
        error_type = "python_exception"
        last_line = traceback.strip().splitlines()[-1]
        message = last_line
        action = RECOMMENDED_ACTIONS["python_exception"]
    else:
        for name, pattern in ERROR_PATTERNS:
            match = pattern.search(text)
            if not match:
                continue
            error_type = name
            if name == "shell_exit" and len(text.splitlines()) > 1:
                # Prefer the last non-empty log line before the generic exit message.
                candidates = [ln.strip() for ln in text.splitlines() if ln.strip()]
                for line in reversed(candidates):
                    if "Process completed with exit code" not in line and not line.startswith("##["):
                        message = line
                        break
                else:
                    message = f"Process exited with code {match.group(1)}"
            elif name == "missing_env" and match.groups():
                var = match.group(1)
                message = f"Missing required environment variable or secret: {var}"
            else:
                message = match.group(0).strip()
            action = RECOMMENDED_ACTIONS.get(name, RECOMMENDED_ACTIONS["unknown"])
            break

    if not failed_step:
        failed_step = _find_failed_step_hint(text) or "Unknown step"

    return {
        "error_type": error_type,
        "error_message": message[:2000],
        "failed_step": failed_step,
        "action_required": action,
        "traceback_excerpt": (traceback or "")[:4000],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract workflow failure details from logs.")
    parser.add_argument("--log-file", type=Path, default=None, help="Path to captured step output log")
    parser.add_argument("--failed-step", default="", help="Name of the step that failed")
    parser.add_argument("--output-file", type=Path, default=None, help="Write JSON result to this file")
    args = parser.parse_args()

    stdin_text = sys.stdin.read() if not sys.stdin.isatty() else ""
    text = _read_log(args.log_file, stdin_text)
    result = extract_error(text, failed_step=args.failed_step)

    payload = json.dumps(result, indent=2)
    print(payload)

    if args.output_file:
        args.output_file.parent.mkdir(parents=True, exist_ok=True)
        args.output_file.write_text(payload, encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
