---
name: github-workflow-monitor
description: Integrate automationbot-art/github-monitors into cron workflow YAML ONLY. All repos write to ONE central BigQuery table. Never create per-repo tables or copy setup scripts.
---

# GitHub Workflow Monitor Integration

## Private repos — fix `repository not found` first

See `docs/SECRETS-AND-PRIVATE-REPOS.md` in github-monitors.

Make **github-monitors** public (recommended) OR enable org Actions access to that private repo.

## One central table

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

**Never** in cron repos:
- Create BigQuery datasets/tables
- Copy `setup_bigquery.py` or `config/bigquery.json`
- Add BigQuery setup workflows

Only edit `.github/workflows/*.yml`.

## Org secret (once)

`LIVESTORE_SA_BASE64` on **automationbot-art** org.

## Do not change schedule

Leave commented cron and `workflow_dispatch` exactly as they are.

## YAML changes only

### Run step

```yaml
- name: <keep name>
  id: cron
  run: |
    set -o pipefail
    python script.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
    ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
    echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

### Monitor step (inserts into central table)

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
  with:
    gcp-credentials-json: ${{ secrets.LIVESTORE_SA_BASE64 }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: <exact step name>
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
    schedule-status: manual-only
```

Omit `schedule-status` if repo has active cron. Omit entire monitor block duplication — one monitor per run step.

## Full guide

`docs/INTEGRATE-EVERY-REPO.md` and `docs/DO-NOT-CREATE-TABLES.md`
