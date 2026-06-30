# Cursor task: Integrate GitHub Workflow Monitor (BigQuery)

> **Temporary file** — delete after Cursor finishes editing workflow YAML.

## Command to give Cursor

```
Read CURSOR-INTEGRATE-MONITOR.md and follow skills/github-workflow-monitor/SKILL.md exactly.

Integrate BigQuery workflow monitoring into all scheduled cron workflows under .github/workflows/.
Use gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }} — do NOT add Slack.
Summarize changes, then delete this file.
```

## Monitor action

```yaml
uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
with:
  gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
  workflow-status: ${{ steps.cron.outcome }}
  failed-step: <exact run step name>
  log-file: ${{ runner.temp }}/cron-output.log
  records-processed: ${{ steps.cron.outputs.records-processed }}
```

## Org secret (already configured once)

`LIVESTORE_SA_JSON` — do not create per-repo copies.

## Slack

Disabled. Do not add `SLACK_WEBHOOK_URL` or Slack steps.

## Full skill reference

See `skills/github-workflow-monitor/SKILL.md` in the github-monitor repo.
