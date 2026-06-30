# github-monitor

Central monitoring for **all** automationbot-art cron repos.

## Where data lives (one place)

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

| | |
|---|---|
| **All repos** | Insert rows into this **one table** |
| **Looker Studio** | Connect to this table, filter by `repository_name` |
| **Cron repos** | YAML changes only — **no** local BigQuery setup |

## Cron repo integration

**[docs/INTEGRATE-EVERY-REPO.md](docs/INTEGRATE-EVERY-REPO.md)** — what to paste in each repo

**[docs/DO-NOT-CREATE-TABLES.md](docs/DO-NOT-CREATE-TABLES.md)** — stop per-repo table creation

## Org secret (once)

`LIVESTORE_SA_JSON` on **automationbot-art** org

## Docs

- [docs/bigquery.md](docs/bigquery.md) — columns (PKT, manual/scheduled)
- [skills/](skills/) — Cursor agent skills

**Repo:** [automationbot-art/github-monitor](https://github.com/automationbot-art/github-monitor)
