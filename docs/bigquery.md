# BigQuery monitoring for Looker Studio (PKT)

All schedule and run times are stored in **Pakistan Standard Time (PKT / Asia/Karachi)** alongside UTC for Looker dashboards.

## Primary Looker filters

| Column | Use |
| --- | --- |
| `run_date_pkt` | **Main date filter** (your local calendar day) |
| `scheduled_time_pkt_label` | Readable scheduled time in tables |
| `dashboard_status` | Scorecard: `Ran — Success`, `Ran — Failed`, `Pending` |
| `needs_attention` | Boolean filter for action queue |
| `operator_instruction` | What to do next — show in detail tables |
| `severity` | Color coding: `success`, `warning`, `error`, `info` |

## Schedule columns (PKT)

| Column | Type | Description |
| --- | --- | --- |
| `timezone` | STRING | `Asia/Karachi` |
| `timezone_label` | STRING | `PKT` |
| `run_date_pkt` | DATE | Run date in PKT |
| `scheduled_time_pkt` | DATETIME | Scheduled start wall clock (PKT) |
| `scheduled_time_pkt_label` | STRING | e.g. `30 Jun 2026, 11:00 AM PKT` |
| `started_at_pkt` | DATETIME | Actual start (PKT) |
| `ended_at_pkt` | DATETIME | Actual end (PKT) |
| `day_of_week_pkt` | STRING | Monday, Tuesday, … |
| `hour_of_day_pkt` | INT64 | 0–23 for heatmaps |
| `cron_description_pkt` | STRING | e.g. `Daily at 11:00 AM PKT` |
| `scheduled_cron` | STRING | Raw cron (UTC on GitHub) |

> GitHub cron is always UTC. `cron 0 6 * * *` = **11:00 AM PKT**.

## Operator / instruction columns

| Column | When populated | Example |
| --- | --- | --- |
| `operator_instruction` | Every run | `No action needed — monitor the next scheduled run.` |
| `action_required` | Failures | `Add the missing secret or repository variable…` |
| `remarks` | Every run | `Failed — ValueError: missing TABLE` |
| `needs_attention` | Failures, warnings, late, 0 records | `true` / `false` |
| `severity` | Every run | `error`, `warning`, `success` |
| `is_late_run` | Scheduled runs | `true` if started >15 min late |
| `delay_minutes` | Scheduled runs | Minutes after expected cron time |
| `dashboard_status` | Every run | `Ran — Success` |

### `operator_instruction` logic

| Situation | Instruction |
| --- | --- |
| Success | No action needed — monitor the next scheduled run. |
| Success + warnings | Review warnings and confirm data quality. |
| Success + 0 records | Verify source data and script filters. |
| Late run | Check Actions queue or runner availability. |
| Failure | Uses `action_required` or parsed error message. |
| Cancelled | Re-trigger manually if still needed. |

## Core columns (unchanged)

| Column | Description |
| --- | --- |
| `repository_name` | `org/repo` |
| `workflow_name` | Workflow name |
| `execution_status` | `Ran` or `Pending` (future) |
| `workflow_outcome` | `success`, `failure`, `cancelled` |
| `records_processed` | Row count from cron script |
| `error_message` | Parsed error |
| `run_url` | GitHub Actions link |

## Looker Studio chart ideas

1. **Today's attention queue** — filter `needs_attention = true` AND `run_date_pkt = today`
2. **Success rate by repo** — `dashboard_status` breakdown
3. **Runs by hour (PKT)** — `hour_of_day_pkt` bar chart
4. **Late runs** — `is_late_run = true` table with `delay_minutes`
5. **Instruction table** — `repository_name`, `scheduled_time_pkt_label`, `operator_instruction`, `run_url`

## Example query (PKT)

```sql
SELECT
  run_date_pkt,
  scheduled_time_pkt_label,
  repository_name,
  workflow_name,
  dashboard_status,
  cron_description_pkt,
  remarks,
  operator_instruction,
  severity,
  needs_attention,
  records_processed,
  run_url
FROM `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
WHERE run_date_pkt >= DATE_SUB(CURRENT_DATE('Asia/Karachi'), INTERVAL 14 DAY)
ORDER BY started_at_pkt DESC
```

## Schema updates

After pulling latest code:

```bash
python scripts/setup_bigquery.py
```

This adds new PKT and instruction columns to the existing table.
