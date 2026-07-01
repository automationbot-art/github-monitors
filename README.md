# github-monitors

Central monitoring for automationbot-art cron repos.

**GitHub repo:** [automationbot-art/github-monitors](https://github.com/automationbot-art/github-monitors)

## Which workflows to run?

**[docs/WHICH-WORKFLOWS-TO-RUN.md](docs/WHICH-WORKFLOWS-TO-RUN.md)**

| Repo | What to run |
| --- | --- |
| **github-monitors** (this repo) | Setup BigQuery (once) → Monitor Self Test (optional) |
| **livestore_data_web** (cron repo) | **daily-warehouse** — your real workflow |

## Secret (org, once)

`LIVESTORE_SA_JSON` — full service account JSON

## Action path for cron repos

```yaml
uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
```

## Central BigQuery table

`combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`

## Docs

- [SECRETS-AND-PRIVATE-REPOS.md](docs/SECRETS-AND-PRIVATE-REPOS.md)
- [INTEGRATE-EVERY-REPO.md](docs/INTEGRATE-EVERY-REPO.md)
