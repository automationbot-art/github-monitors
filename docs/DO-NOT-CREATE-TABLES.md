# ⛔ CRON REPOS: DO NOT CREATE BIGQUERY TABLES

This file exists so Cursor/agents stop creating per-repo BigQuery resources.

## One table for everything

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

## Cron repos may ONLY

- Edit `.github/workflows/*.yml`
- Add `Workflow monitor` step pointing at `automationbot-art/github-monitor`

## Cron repos must NEVER

- Run `setup_bigquery.py`
- Add `config/bigquery.json`
- Create datasets or tables named after the repo
- Copy scripts from `github-monitor` into the cron repo

Setup and table creation happen **once** in the `automationbot-art/github-monitor` repository only.

See [INTEGRATE-EVERY-REPO.md](INTEGRATE-EVERY-REPO.md).
