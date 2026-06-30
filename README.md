# github-monitor

Reusable GitHub Actions monitoring for scheduled cron workflows. **BigQuery + Looker Studio** — Slack disabled for now.

**Repo:** [automationbot-art/github-monitor](https://github.com/automationbot-art/github-monitor)

## Documentation

- **[docs/INTEGRATE-EVERY-REPO.md](docs/INTEGRATE-EVERY-REPO.md)** — what to paste in every cron repo
- [docs/setup.md](docs/setup.md) — overview
- [docs/bigquery.md](docs/bigquery.md) — Looker columns (PKT + manual/scheduled)

## BigQuery target

`combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`

## Org secret (one place)

`LIVESTORE_SA_JSON` — GCP service account JSON for all cron repos

## Components

| Component | Purpose |
| --- | --- |
| `.github/actions/workflow-monitor` | Summary, artifact, BigQuery insert |
| `scripts/setup_bigquery.py` | Create dataset + table |
| `skills/github-workflow-monitor` | Roll out monitor to cron repos |

## License

MIT
