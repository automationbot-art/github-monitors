# What to paste in every cron repo

Copy this guide into each repository (or give it to Cursor), then delete after integration.

---

## One-time (org level — already done)

| Secret | Where |
| --- | --- |
| `LIVESTORE_SA_JSON` | **automationbot-art** org → Settings → Secrets → Actions |

Do **not** add this secret per repo.

---

## Rules — read before editing YAML

| Rule | Detail |
| --- | --- |
| **Do NOT change `on:` schedule** | If cron lines are commented out or removed, **leave them exactly as they are** |
| **Do NOT uncomment schedule** | Many repos run manually only — that is fine |
| **Do NOT change triggers** | Keep `workflow_dispatch`, commented `# schedule:`, etc. untouched |
| **Only add** | Log capture on the Python run step + Workflow monitor step at the end |

---

## Paste block 1 — Update your Python run step

Find the step that runs your script (e.g. `Run cron job`, `Append rankings`). **Only change this step:**

```yaml
      - name: Run cron job
        id: cron
        run: |
          set -o pipefail
          python main.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
          ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          if [ -z "${ROWS}" ]; then
            ROWS="$(grep -oE 'records_processed=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          fi
          echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

- Keep your original step **name** (change `Run cron job` only if yours is different)
- Keep your original `python ...` command
- Add `id: cron` if not present

---

## Paste block 2 — Add monitor step (end of same job)

Add **immediately after** the run step:

### If repo runs on **manual trigger only** (schedule commented/disabled)

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
          schedule-status: manual-only
```

### If repo has **active daily cron** (schedule not commented)

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

> Omit `schedule-status` when cron is active — it auto-detects.

---

## Matrix workflows (multiple jobs)

Add **both blocks to each job** that runs Python. Use the correct `failed-step` name per job.

Example — manual-only repo with two jobs:

| Job | `failed-step` | `schedule-status` |
| --- | --- | --- |
| `rankings` | `Append rankings` | `manual-only` |
| `launches` | `Append new launches + top new free` | `manual-only` |

---

## Example: manual-only workflow (schedule commented — do not change)

```yaml
on:
  # schedule:
  #   - cron: "0 6 * * *"
  workflow_dispatch:

jobs:
  daily:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # ... your existing setup steps — do not change ...

      - name: Run cron job
        id: cron
        run: |
          set -o pipefail
          python main.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
          ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"

      - name: Workflow monitor
        if: always()
        uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
        with:
          gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
          workflow-status: ${{ steps.cron.outcome }}
          failed-step: Run cron job
          log-file: ${{ runner.temp }}/cron-output.log
          records-processed: ${{ steps.cron.outputs.records-processed }}
          schedule-status: manual-only
```

---

## Cursor prompt (copy into each repo)

```
Read docs/INTEGRATE-EVERY-REPO.md (or CURSOR-INTEGRATE-MONITOR.md) from github-monitor.

Integrate workflow monitoring into .github/workflows/ Python jobs ONLY.

CRITICAL: Do NOT change, uncomment, or add schedule/cron lines. Leave workflow_dispatch
and commented schedules exactly as they are. Many repos are manual-run only.

For each Python run step: add id:cron, tee log capture, records-processed output.
After each run step: add Workflow monitor with LIVESTORE_SA_JSON.
If schedule is commented/disabled: add schedule-status: manual-only.

Do not add Slack. Summarize changes when done.
```

---

## What gets stored in BigQuery (Looker)

| Column | Manual run | Scheduled run |
| --- | --- | --- |
| `run_mode` | `Manual` | `Scheduled` |
| `trigger_type_label` | `Manual Run` | `Scheduled Cron` |
| `schedule_status` | `Disabled (manual only)` | `Active` |
| `is_manual_run` | `true` | `false` |
| `dashboard_status` | `Manual — Success` | `Ran — Success` |
| `remarks` | `Manual run — Successful…` | `Successful…` |
| `scheduled_time_pkt_label` | Actual run time (PKT) | Scheduled/run time (PKT) |

---

## Checklist per repo

- [ ] Run step has `id: cron` + `tee` log capture
- [ ] Monitor step added with `if: always()`
- [ ] `schedule-status: manual-only` if cron is commented/disabled
- [ ] Schedule/cron lines **unchanged**
- [ ] Run workflow manually once → check BigQuery / Looker for new row
