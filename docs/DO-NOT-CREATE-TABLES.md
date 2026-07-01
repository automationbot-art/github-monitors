# Cron repos: do not create BigQuery tables

**One table for everything:**

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

Cron repos may **only** edit `.github/workflows/*.yml` and add the remote `Workflow monitor` step.

**Never** copy `setup_bigquery.py`, `config/bigquery.json`, or create repo-named tables.

Setup runs once in **automationbot-art/github-monitors** only.
