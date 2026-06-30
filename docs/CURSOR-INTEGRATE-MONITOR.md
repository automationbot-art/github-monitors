# Cursor: integrate github-monitor (YAML only)

> Delete this file after Cursor finishes.

## Prompt

```
Integrate github-monitor into .github/workflows/ — YAML CHANGES ONLY.

⛔ DATA STORAGE — ONE CENTRAL TABLE FOR ALL REPOS:
  combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events

DO NOT in this repo:
- Create BigQuery datasets or tables
- Copy setup_bigquery.py, insert_workflow_run.py, or config/bigquery.json
- Add BigQuery setup workflows or Python monitoring scripts

ONLY add to existing workflow YAML:
1. Run step: id:cron + tee log + records-processed
2. Workflow monitor step:
   uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
   gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
   schedule-status: manual-only  (if cron schedule is commented/disabled)

DO NOT change schedule/cron lines. Leave manual-only triggers as-is.
No Slack. Summarize YAML edits only.
```

## Central table (all repos)

| Field | Value |
| --- | --- |
| Project | `combine-data-pipeline-482809` |
| Dataset | `github_cron_monitoring` |
| Table | `workflow_run_events` |

Filter Looker by `repository_name` — not separate tables per repo.
