---
name: github-workflow-monitor
description: Integrate automationbot-art/github-monitor into cron workflow YAML. Use when rolling out BigQuery monitoring. Never uncomment or change commented schedule lines.
---

# GitHub Workflow Monitor Integration

## Critical rule

**Do NOT change schedule/cron configuration.**

- If `schedule:` is commented out → leave it commented
- If only `workflow_dispatch` is active → leave it as manual-only
- Only add log capture + monitor steps

## Org secret (once)

`LIVESTORE_SA_JSON` on **automationbot-art** org — not per repo.

## Change 1 — Run step

```yaml
- name: <keep original name>
  id: cron
  run: |
    set -o pipefail
    python your_script.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
    ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
    echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

## Change 2 — Monitor step

**Manual-only repo** (schedule commented/disabled):

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: <exact step name>
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
    schedule-status: manual-only
```

**Active cron repo** — same but omit `schedule-status`.

## Full paste guide

See `docs/INTEGRATE-EVERY-REPO.md`.
