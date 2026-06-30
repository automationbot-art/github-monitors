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

## Key columns for Looker Studio (PKT)

| Column | Use in dashboard |
| --- | --- |
| `run_date_pkt` | **Primary date filter** (Pakistan time) |
| `scheduled_time_pkt_label` | Readable schedule time in tables |
| `cron_description_pkt` | e.g. Daily at 11:00 AM PKT |
| `dashboard_status` | Ran — Success / Ran — Failed / Pending |
| `operator_instruction` | Actionable next step for operators |
| `needs_attention` | Filter attention queue |
| `severity` | success / warning / error / info |
| `is_late_run` | Late schedule detection |
| `hour_of_day_pkt` | PKT heatmap by hour |
| `remarks` | Human-readable outcome |
| `run_url` | Drill-through to GitHub |

## Remarks values

- `Successful — completed without errors`
- `Successful with warnings: ...`
- `Failed — <error message>`

## Pending status (future)

`execution_status = Pending` will be populated by a future sync job that compares expected cron schedules vs actual runs. Current monitor writes `Ran` on every completed job.

## Query example

```sql
SELECT
  run_date_pkt,
  scheduled_time_pkt_label,
  repository_name,
  workflow_name,
  dashboard_status,
  operator_instruction,
  severity,
  needs_attention,
  records_processed,
  run_url
FROM `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
WHERE run_date_pkt >= DATE_SUB(CURRENT_DATE('Asia/Karachi'), INTERVAL 30 DAY)
ORDER BY started_at_pkt DESC
```
