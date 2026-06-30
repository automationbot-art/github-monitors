---
name: bigquery-looker-dashboard
description: Provision and query the github_cron_monitoring BigQuery dataset for Looker Studio dashboards. Use when setting up tables, running setup_bigquery.py, or connecting Looker to workflow run data.
---

# BigQuery + Looker Studio Monitoring

## Resources

| Item | Value |
| --- | --- |
| GCP project | `combine-data-pipeline-482809` |
| Dataset | `github_cron_monitoring` |
| Table | `workflow_run_events` |
| Credentials (local) | `config/livestore.json` |
| Config (no secrets) | `config/bigquery.json` |

## Provision dataset + table

### Locally

```bash
pip install -r requirements.txt
python scripts/setup_bigquery.py --config config/bigquery.json --credentials config/livestore.json
```

### GitHub Actions

Run workflow **Setup BigQuery Monitoring** (requires `LIVESTORE_SA_JSON` secret).

## Key columns for Looker Studio

| Column | Use in dashboard |
| --- | --- |
| `run_date` | Date filter, time series |
| `repository_name` | Repo breakdown |
| `workflow_name` | Workflow filter |
| `scheduled_time_utc` | Schedule adherence |
| `execution_status` | Ran vs Pending (future sync) |
| `workflow_outcome` | success / failure / cancelled |
| `remarks` | Human-readable status for tables |
| `error_message` | Failure detail cards |
| `records_processed` | Volume metrics |
| `has_warnings` | Warning filter |
| `run_url` | Drill-through link |

## Remarks values

- `Successful — completed without errors`
- `Successful with warnings: ...`
- `Failed — <error message>`

## Pending status (future)

`execution_status = Pending` will be populated by a future sync job that compares expected cron schedules vs actual runs. Current monitor writes `Ran` on every completed job.

## Query example

```sql
SELECT
  run_date,
  repository_name,
  workflow_name,
  scheduled_time_utc,
  execution_status,
  workflow_outcome,
  remarks,
  records_processed,
  run_url
FROM `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
WHERE run_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
ORDER BY recorded_at DESC
```
