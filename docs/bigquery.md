# BigQuery monitoring for Looker Studio

## Overview

Every monitored workflow run inserts one row into BigQuery. Looker Studio connects to this table for cross-repo cron dashboards.

```
GitHub Actions (cron repos)
        │
        ▼
workflow-monitor action
        │
        ├── GITHUB_STEP_SUMMARY + artifact (unchanged)
        └── INSERT → github_cron_monitoring.workflow_run_events
                              │
                              ▼
                      Looker Studio dashboard
```

## Dataset and table

| Resource | ID | Description |
| --- | --- | --- |
| Dataset | `github_cron_monitoring` | Scheduled GitHub Actions monitoring across automationbot-art repos |
| Table | `workflow_run_events` | One row per monitored job execution |

**Full table ID:** `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`

Partitioned by `run_date`, clustered by `repository_name`, `workflow_outcome`, `execution_status`.

## Column reference

| Column | Type | Description |
| --- | --- | --- |
| `event_id` | STRING | Unique row UUID |
| `recorded_at` | TIMESTAMP | When the row was written |
| `run_date` | DATE | Run date (UTC) — primary Looker date filter |
| `repository_name` | STRING | `org/repo` |
| `repository_short_name` | STRING | Repo name only |
| `workflow_name` | STRING | Workflow display name |
| `job_name` | STRING | Job name within workflow |
| `branch` | STRING | Git branch |
| `commit_sha` | STRING | Commit SHA |
| `trigger_type` | STRING | `schedule`, `workflow_dispatch`, etc. |
| `scheduled_cron` | STRING | Cron expression |
| `scheduled_time_utc` | TIMESTAMP | Scheduled/actual start (UTC) |
| `started_at` | TIMESTAMP | Job start |
| `ended_at` | TIMESTAMP | Job end |
| `duration_seconds` | INT64 | Duration |
| `execution_status` | STRING | `Ran` (executed) or `Pending` (future sync) |
| `workflow_outcome` | STRING | `success`, `failure`, `cancelled` |
| `remarks` | STRING | Human summary for Looker tables |
| `error_message` | STRING | Parsed error text |
| `error_type` | STRING | Error classification |
| `failed_step` | STRING | Failed Actions step name |
| `action_required` | STRING | Recommended fix |
| `records_processed` | INT64 | Rows/records from cron script |
| `warnings` | STRING | Warning text |
| `has_warnings` | BOOL | True if warnings on success |
| `github_run_id` | STRING | Actions run ID |
| `github_run_number` | INT64 | Run number |
| `github_run_attempt` | INT64 | Re-run attempt |
| `run_url` | STRING | Link to GitHub run |
| `artifact_url` | STRING | Link to summary artifact |
| `log_excerpt` | STRING | Truncated log tail |
| `ingestion_source` | STRING | `github-actions-workflow-monitor` |

## Setup

### 1. Credentials

Local: copy `config/livestore.json.example` → `config/livestore.json` (gitignored).

GitHub: org secret **`LIVESTORE_SA_JSON`** with the full JSON content.

Service account needs:

- `bigquery.datasets.create` (setup only)
- `bigquery.tables.create` (setup only)
- `bigquery.tables.updateData` (insert rows)

### 2. Create dataset + table

```bash
pip install -r requirements.txt
python scripts/setup_bigquery.py
```

Or run GitHub workflow **Setup BigQuery Monitoring**.

### 3. Connect Looker Studio

1. Looker Studio → **Create** → **BigQuery** connector
2. Select project `combine-data-pipeline-482809`
3. Table `github_cron_monitoring.workflow_run_events`
4. Build charts: failures by repo, daily success rate, remarks table, records processed

## Slack (disabled)

Slack notification steps are commented out in the composite action. Re-enable when ready.
