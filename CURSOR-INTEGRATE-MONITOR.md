# Cursor task: Integrate GitHub Workflow Monitor

> **Temporary file** — delete after Cursor finishes. Full guide: `docs/INTEGRATE-EVERY-REPO.md`

## Cursor prompt (paste this)

```
Read CURSOR-INTEGRATE-MONITOR.md and docs/INTEGRATE-EVERY-REPO.md in github-monitor.

Integrate workflow monitoring into .github/workflows/ Python jobs ONLY.

CRITICAL — DO NOT CHANGE SCHEDULE:
- Leave commented cron lines as they are (do not uncomment)
- Leave workflow_dispatch as the only trigger if that is how the repo works
- Do NOT add or enable daily schedule unless already active

For each Python run step:
1. Add id: cron (unique per job if multiple run steps)
2. Pipe output: set -o pipefail + tee to ${RUNNER_TEMP}/cron-output.log
3. Parse rows~= or records_processed= → records-processed output

After each run step, add Workflow monitor:
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
  schedule-status: manual-only   ← ONLY if cron schedule is commented/disabled

Do NOT add Slack. Summarize files changed, then delete this file.
```

## Monitor step — manual-only repos (schedule commented)

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: <exact run step name>
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
    schedule-status: manual-only
```

## Monitor step — active cron repos

Same as above but **omit** `schedule-status`.

## Org secret (once, not per repo)

`LIVESTORE_SA_JSON`
