# GitHub Actions Workflow Monitor

Centralized monitoring for scheduled cron workflows. Stores run data in **BigQuery** for **Looker Studio** dashboards.

## What this does

- **Job Summary** on every run (`GITHUB_STEP_SUMMARY` + `media/workflow-summary.md` artifact)
- **BigQuery row** per run in `github_cron_monitoring.workflow_run_events`
- **Slack** — disabled (commented out in action; enable later)

## Architecture

```
github-monitor/
├── .github/actions/workflow-monitor/   # Composite action
├── config/bigquery.json                # Dataset/table names (no secrets)
├── config/livestore.json               # Local SA creds (gitignored)
├── scripts/                            # setup + insert scripts
├── skills/                             # Harness-style agent skills
└── docs/bigquery.md                    # Looker column reference
```

## One-time setup

### 1. Org secret (one place for all repos)

| Secret | Value |
| --- | --- |
| `LIVESTORE_SA_JSON` | Full contents of `config/livestore.json` |

GitHub → **automationbot-art** → **Settings** → **Secrets** → **Actions** → New organization secret.

### 2. Provision BigQuery

```bash
pip install -r requirements.txt
python scripts/setup_bigquery.py
```

Or run workflow **Setup BigQuery Monitoring** in this repo.

### 3. Add monitor to cron workflows

See [docs/setup.md](setup.md) and [skills/github-workflow-monitor/SKILL.md](../skills/github-workflow-monitor/SKILL.md).

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: Run cron job
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
```

## Looker Studio

Connect to:

`combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`

Full column docs: [bigquery.md](bigquery.md)

## Skills (Harness-style)

| Skill | Purpose |
| --- | --- |
| `skills/github-workflow-monitor` | Integrate monitor into cron YAML files |
| `skills/bigquery-looker-dashboard` | BQ setup and Looker queries |

## Testing

1. Add `LIVESTORE_SA_JSON` org secret
2. Run **Setup BigQuery Monitoring**
3. Run **Monitor Self Test** (optionally with simulate failure)
