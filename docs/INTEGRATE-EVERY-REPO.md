# What to paste in every cron repo

> **Private repos:** read [SECRETS-AND-PRIVATE-REPOS.md](SECRETS-AND-PRIVATE-REPOS.md) first or you will get `repository not found`.

---

## WHERE DATA IS STORED

**One central BigQuery table for all repos:**

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

Cron repos: **YAML only** — no BigQuery scripts, no new tables. See [DO-NOT-CREATE-TABLES.md](DO-NOT-CREATE-TABLES.md).

---

## Secret (org level, once)

| Secret | Value |
| --- | --- |
| `LIVESTORE_SA_JSON` | Full `config/livestore.json` content |

**automationbot-art** → Settings → Secrets → Actions → All repositories.

---

## YAML only — do not touch schedule

Leave commented `# schedule:` and `workflow_dispatch` **unchanged**.

### 1. Run step

```yaml
      - name: Run cron job
        id: cron
        run: |
          set -o pipefail
          python main.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
          ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
          echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

### 2. Monitor step (manual-only repos)

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

Omit `schedule-status` if active cron. Omit entire block duplication — one monitor per run step.

---

## Cursor prompt

```
YAML ONLY. One table: combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
No BigQuery scripts/tables in this repo. Do not change schedule lines.
uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
schedule-status: manual-only if cron commented.
```
