#!/usr/bin/env python3
"""Create BigQuery dataset and workflow_run_events table for Looker Studio."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account


def load_config(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def get_client(credentials_path: Path, project_id: str) -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    return bigquery.Client(credentials=credentials, project=project_id)


def table_schema() -> list[bigquery.SchemaField]:
    return [
        bigquery.SchemaField(
            "event_id",
            "STRING",
            mode="REQUIRED",
            description="Unique UUID for this monitoring event row.",
        ),
        bigquery.SchemaField(
            "recorded_at",
            "TIMESTAMP",
            mode="REQUIRED",
            description="UTC timestamp when this row was written to BigQuery.",
        ),
        bigquery.SchemaField(
            "run_date",
            "DATE",
            mode="REQUIRED",
            description="Calendar date of the workflow run (UTC).",
        ),
        bigquery.SchemaField(
            "run_date_pkt",
            "DATE",
            mode="NULLABLE",
            description="Calendar date in Pakistan Standard Time (PKT) — primary Looker date filter.",
        ),
        bigquery.SchemaField(
            "timezone",
            "STRING",
            mode="NULLABLE",
            description="IANA timezone used for local schedule display (Asia/Karachi).",
        ),
        bigquery.SchemaField(
            "timezone_label",
            "STRING",
            mode="NULLABLE",
            description="Short timezone label shown on dashboards (PKT).",
        ),
        bigquery.SchemaField(
            "repository_name",
            "STRING",
            mode="REQUIRED",
            description="Full GitHub repository (org/repo).",
        ),
        bigquery.SchemaField(
            "repository_short_name",
            "STRING",
            mode="NULLABLE",
            description="Repository name without org prefix.",
        ),
        bigquery.SchemaField(
            "workflow_name",
            "STRING",
            mode="REQUIRED",
            description="GitHub Actions workflow name.",
        ),
        bigquery.SchemaField(
            "job_name",
            "STRING",
            mode="NULLABLE",
            description="GitHub Actions job name within the workflow.",
        ),
        bigquery.SchemaField(
            "branch",
            "STRING",
            mode="NULLABLE",
            description="Git ref branch that ran.",
        ),
        bigquery.SchemaField(
            "commit_sha",
            "STRING",
            mode="NULLABLE",
            description="Git commit SHA for the run.",
        ),
        bigquery.SchemaField(
            "trigger_type",
            "STRING",
            mode="NULLABLE",
            description="GitHub event trigger: schedule, workflow_dispatch, push, etc.",
        ),
        bigquery.SchemaField(
            "trigger_type_label",
            "STRING",
            mode="NULLABLE",
            description="Human-readable trigger for Looker: Manual Run, Scheduled Cron, etc.",
        ),
        bigquery.SchemaField(
            "run_mode",
            "STRING",
            mode="NULLABLE",
            description="Manual, Scheduled, or Other — how this run was started.",
        ),
        bigquery.SchemaField(
            "is_manual_run",
            "BOOL",
            mode="NULLABLE",
            description="True when triggered via workflow_dispatch (Run workflow button).",
        ),
        bigquery.SchemaField(
            "is_scheduled_run",
            "BOOL",
            mode="NULLABLE",
            description="True when triggered by an active cron schedule.",
        ),
        bigquery.SchemaField(
            "schedule_status",
            "STRING",
            mode="NULLABLE",
            description="Active, Disabled (manual only), or Manual trigger — reflects cron config state.",
        ),
        bigquery.SchemaField(
            "scheduled_cron",
            "STRING",
            mode="NULLABLE",
            description="Cron expression when triggered by schedule (GitHub uses UTC).",
        ),
        bigquery.SchemaField(
            "cron_description_pkt",
            "STRING",
            mode="NULLABLE",
            description="Human-readable schedule in PKT, e.g. Daily at 11:00 AM PKT.",
        ),
        bigquery.SchemaField(
            "scheduled_time_utc",
            "TIMESTAMP",
            mode="NULLABLE",
            description="Scheduled or actual start time in UTC.",
        ),
        bigquery.SchemaField(
            "expected_run_time_utc",
            "TIMESTAMP",
            mode="NULLABLE",
            description="Expected cron trigger time in UTC for delay calculation.",
        ),
        bigquery.SchemaField(
            "scheduled_time_pkt",
            "DATETIME",
            mode="NULLABLE",
            description="Scheduled start wall-clock time in PKT.",
        ),
        bigquery.SchemaField(
            "scheduled_time_pkt_label",
            "STRING",
            mode="NULLABLE",
            description="Formatted scheduled time for Looker tables, e.g. 30 Jun 2026, 11:00 AM PKT.",
        ),
        bigquery.SchemaField(
            "started_at",
            "TIMESTAMP",
            mode="NULLABLE",
            description="Workflow job start time (UTC).",
        ),
        bigquery.SchemaField(
            "started_at_pkt",
            "DATETIME",
            mode="NULLABLE",
            description="Workflow job start wall-clock time in PKT.",
        ),
        bigquery.SchemaField(
            "ended_at",
            "TIMESTAMP",
            mode="NULLABLE",
            description="Workflow job end time (UTC).",
        ),
        bigquery.SchemaField(
            "ended_at_pkt",
            "DATETIME",
            mode="NULLABLE",
            description="Workflow job end wall-clock time in PKT.",
        ),
        bigquery.SchemaField(
            "day_of_week_pkt",
            "STRING",
            mode="NULLABLE",
            description="Day name in PKT for weekly Looker breakdowns.",
        ),
        bigquery.SchemaField(
            "hour_of_day_pkt",
            "INT64",
            mode="NULLABLE",
            description="Hour 0-23 in PKT for heatmaps and peak-time charts.",
        ),
        bigquery.SchemaField(
            "duration_seconds",
            "INT64",
            mode="NULLABLE",
            description="Job duration in seconds.",
        ),
        bigquery.SchemaField(
            "is_late_run",
            "BOOL",
            mode="NULLABLE",
            description="True when the job started more than 15 minutes after expected cron time.",
        ),
        bigquery.SchemaField(
            "delay_minutes",
            "INT64",
            mode="NULLABLE",
            description="Minutes after expected schedule time the job actually started.",
        ),
        bigquery.SchemaField(
            "execution_status",
            "STRING",
            mode="REQUIRED",
            description="Ran = job executed; Pending = expected but not yet observed (future sync).",
        ),
        bigquery.SchemaField(
            "dashboard_status",
            "STRING",
            mode="NULLABLE",
            description="Combined status for Looker scorecards: Ran — Success, Ran — Failed, Pending.",
        ),
        bigquery.SchemaField(
            "workflow_outcome",
            "STRING",
            mode="NULLABLE",
            description="GitHub outcome: success, failure, cancelled, skipped.",
        ),
        bigquery.SchemaField(
            "remarks",
            "STRING",
            mode="NULLABLE",
            description="Human-readable summary for Looker: success/failure details and warnings.",
        ),
        bigquery.SchemaField(
            "error_message",
            "STRING",
            mode="NULLABLE",
            description="Extracted error message when the workflow failed.",
        ),
        bigquery.SchemaField(
            "error_type",
            "STRING",
            mode="NULLABLE",
            description="Classified error: python_exception, bigquery, auth_failure, timeout, etc.",
        ),
        bigquery.SchemaField(
            "failed_step",
            "STRING",
            mode="NULLABLE",
            description="Name of the GitHub Actions step that failed.",
        ),
        bigquery.SchemaField(
            "action_required",
            "STRING",
            mode="NULLABLE",
            description="Recommended remediation for operators.",
        ),
        bigquery.SchemaField(
            "operator_instruction",
            "STRING",
            mode="NULLABLE",
            description="Short actionable instruction for Looker dashboard operators.",
        ),
        bigquery.SchemaField(
            "severity",
            "STRING",
            mode="NULLABLE",
            description="Dashboard severity: success, warning, error, info.",
        ),
        bigquery.SchemaField(
            "needs_attention",
            "BOOL",
            mode="NULLABLE",
            description="True for failures, warnings, late runs, or zero records processed.",
        ),
        bigquery.SchemaField(
            "records_processed",
            "INT64",
            mode="NULLABLE",
            description="Optional row/record count from the cron script.",
        ),
        bigquery.SchemaField(
            "warnings",
            "STRING",
            mode="NULLABLE",
            description="Non-fatal warnings captured during the run.",
        ),
        bigquery.SchemaField(
            "has_warnings",
            "BOOL",
            mode="NULLABLE",
            description="True when warnings were present on a successful run.",
        ),
        bigquery.SchemaField(
            "github_run_id",
            "STRING",
            mode="NULLABLE",
            description="GitHub Actions run ID.",
        ),
        bigquery.SchemaField(
            "github_run_number",
            "INT64",
            mode="NULLABLE",
            description="GitHub Actions run number.",
        ),
        bigquery.SchemaField(
            "github_run_attempt",
            "INT64",
            mode="NULLABLE",
            description="Re-run attempt number.",
        ),
        bigquery.SchemaField(
            "run_url",
            "STRING",
            mode="NULLABLE",
            description="Direct link to the GitHub Actions run.",
        ),
        bigquery.SchemaField(
            "artifact_url",
            "STRING",
            mode="NULLABLE",
            description="Link to workflow-summary artifact.",
        ),
        bigquery.SchemaField(
            "log_excerpt",
            "STRING",
            mode="NULLABLE",
            description="Truncated log excerpt for quick Looker inspection.",
        ),
        bigquery.SchemaField(
            "ingestion_source",
            "STRING",
            mode="NULLABLE",
            description="Source system that wrote this row.",
        ),
    ]


def ensure_dataset(client: bigquery.Client, project_id: str, dataset_id: str, description: str, location: str) -> None:
    dataset_ref = f"{project_id}.{dataset_id}"
    dataset = bigquery.Dataset(dataset_ref)
    dataset.location = location
    dataset.description = description
    client.create_dataset(dataset, exists_ok=True)
    print(f"Dataset ready: {dataset_ref}")


def ensure_table(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    table_id: str,
    description: str,
) -> None:
    table_ref = f"{project_id}.{dataset_id}.{table_id}"
    desired_schema = table_schema()

    try:
        existing = client.get_table(table_ref)
        merged = list(existing.schema)
        existing_names = {field.name for field in merged}
        added = 0
        for field in desired_schema:
            if field.name not in existing_names:
                merged.append(field)
                added += 1
        if added:
            existing.schema = merged
            client.update_table(existing, ["schema"])
            print(f"Table schema updated: {table_ref} (+{added} columns)")
        else:
            print(f"Table ready: {table_ref}")
    except Exception:
        table = bigquery.Table(table_ref, schema=desired_schema)
        table.description = description
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field="run_date",
        )
        table.clustering_fields = [
            "repository_name",
            "workflow_outcome",
            "needs_attention",
            "run_date_pkt",
        ]
        client.create_table(table)
        print(f"Table created: {table_ref}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Provision BigQuery monitoring dataset and table.")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/bigquery.json"),
        help="Path to non-secret BigQuery config JSON",
    )
    parser.add_argument(
        "--credentials",
        type=Path,
        default=None,
        help="Service account JSON path (default: credentials_file from config)",
    )
    args = parser.parse_args()

    cfg = load_config(args.config)
    credentials_path = args.credentials or Path(cfg["credentials_file"])
    project_id = cfg["project_id"]

    client = get_client(credentials_path, project_id)
    ensure_dataset(
        client,
        project_id,
        cfg["dataset_id"],
        cfg["dataset_description"],
        cfg["location"],
    )
    ensure_table(
        client,
        project_id,
        cfg["dataset_id"],
        cfg["table_id"],
        cfg["table_description"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
