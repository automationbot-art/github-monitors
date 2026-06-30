# Cursor task: Integrate GitHub Workflow Monitor

> **Temporary file** — delete this file after Cursor finishes editing your workflow YAML.

---

## Command to give Cursor

Copy and paste this as your Cursor prompt:

```
Read CURSOR-INTEGRATE-MONITOR.md in this repo and follow every instruction exactly.

Find all scheduled/cron GitHub Actions workflow YAML files under .github/workflows/.
For each Python run step (cron, append, ETL, daily job, etc.):

1. Add id: cron (or id: cron-rankings / id: cron-launches if multiple run steps exist in the SAME job — never duplicate the same id in one job)
2. Pipe stdout/stderr through tee to ${RUNNER_TEMP}/cron-output.log with set -o pipefail
3. Parse rows~= or records_processed= from script output if present and set records-processed step output
4. Append a Workflow monitor step after each run step with if: always()

Use monitor action: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
Use secret: ${{ secrets.SLACK_WEBHOOK_URL }}
Set failed-step to the exact run step name in that job.

Do not change schedule, triggers, matrix config, or unrelated steps.
Show me a summary of files changed, then delete CURSOR-INTEGRATE-MONITOR.md.
```

---

## What Cursor must do

### Target files

- `.github/workflows/*.yml` — any file with `schedule:`, `cron:`, or a daily/scheduled Python job
- Skip: `reusable-*.yml`, `monitor-*.yml`, dependabot, release-only workflows

### Change 1 — Every Python “run” step

**Before (example):**

```yaml
- name: Append rankings
  run: python scripts/append_rankings.py
```

**After:**

```yaml
- name: Append rankings
  id: cron
  run: |
    set -o pipefail
    python scripts/append_rankings.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
    ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
    if [ -z "${ROWS}" ]; then
      ROWS="$(grep -oE 'records_processed=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
    fi
    echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

**Rules:**

| Rule | Detail |
| --- | --- |
| `id` | Use `cron` when one run step per job. If one job has multiple run steps, use unique ids: `cron-rankings`, `cron-launches` and reference matching id in monitor step |
| `tee` | Always `2>&1 \| tee "${RUNNER_TEMP}/cron-output.log"` |
| `pipefail` | Always `set -o pipefail` as first line |
| Row count | Parse `rows~=` or `records_processed=` from log; default `0` |
| Step name | Keep the original `name:` unchanged — `failed-step` must match it exactly |

### Change 2 — Workflow monitor step (immediately after each run step)

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: Append rankings
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
```

**Replace:**

| Placeholder | Value |
| --- | --- |
| `steps.cron` | Same `id` as the run step (`steps.cron-rankings` if id was `cron-rankings`) |
| `failed-step` | Exact `name:` of the run step above |
| `records-processed` | `${{ steps.<same-id>.outputs.records-processed }}` |

### Matrix / multiple jobs

- **Separate jobs** (e.g. `rankings` + `launches` matrix): each job gets its own `id: cron` + monitor block — same `cron` id in different jobs is OK
- **Same job, multiple run steps**: unique ids per step + one monitor step after each run step

### Secrets — do NOT add per repo

`SLACK_WEBHOOK_URL` is an **organization secret** on `automationbot-art`. Workflows only reference `${{ secrets.SLACK_WEBHOOK_URL }}`. Do not create `.env` files or commit webhook URLs.

### Do NOT change

- `on:` schedule / cron expressions
- `strategy.matrix` values
- Checkout, setup-python, pip install, auth steps
- Permissions unless missing `contents: read` (add only if needed)

### After editing

1. List every modified file and what changed
2. Delete this file: `CURSOR-INTEGRATE-MONITOR.md`

---

## Reference: full single-job example

```yaml
jobs:
  daily:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run daily ETL
        id: cron
        run: |
          set -o pipefail
          python main.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
          ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          if [ -z "${ROWS}" ]; then
            ROWS="$(grep -oE 'records_processed=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          fi
          echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"

      - name: Workflow monitor
        if: always()
        uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
        with:
          slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
          workflow-status: ${{ steps.cron.outcome }}
          failed-step: Run daily ETL
          log-file: ${{ runner.temp }}/cron-output.log
          records-processed: ${{ steps.cron.outputs.records-processed }}
```

---

## Monitor action source

- Repo: `automationbot-art/github-monitor`
- Action: `.github/actions/workflow-monitor@main`
- Docs: https://github.com/automationbot-art/github-monitor/blob/main/docs/setup.md
