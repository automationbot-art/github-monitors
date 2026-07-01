# Cursor: integrate monitor (YAML only)

See [SECRETS-AND-PRIVATE-REPOS.md](SECRETS-AND-PRIVATE-REPOS.md) and [INTEGRATE-EVERY-REPO.md](INTEGRATE-EVERY-REPO.md).

```
YAML ONLY. Private org: ensure github-monitors action is accessible (public repo or org Actions access).

ONE TABLE: combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
NO BigQuery scripts/tables in this repo. Do NOT change schedule/cron lines.

Add tee + Workflow monitor:
  uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
  gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
  schedule-status: manual-only (if cron commented)
```
