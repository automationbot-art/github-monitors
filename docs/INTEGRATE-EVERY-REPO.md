# What to paste in every cron repo

---

## WHERE DATA IS STORED (read this first)

**All repositories write to ONE central BigQuery table. There is no per-repo table.**

| What | Value |
| --- | --- |
| **GCP project** | `combine-data-pipeline-482809` |
| **Dataset** | `github_cron_monitoring` |
| **Table** | `workflow_run_events` |
| **Full table ID** | `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events` |
| **Looker Studio** | Connect to this **one table** — filter by `repository_name` |

Every cron repo inserts **rows** into this shared table. The `repository_name` column tells you which repo each row came from (e.g. `automationbot-art/livestore_data_web`).

### DO NOT do this in cron repos

| Forbidden | Why |
| --- | --- |
| **Do NOT create BigQuery datasets or tables** | Table already exists in `github-monitor` |
| **Do NOT copy `setup_bigquery.py`** into cron repos | Setup runs once in `github-monitor` only |
| **Do NOT copy `config/bigquery.json`** into cron repos | Config lives in `github-monitor` action |
| **Do NOT add BigQuery setup workflows** | No `setup-bigquery.yml` in cron repos |
| **Do NOT create repo-named tables** | e.g. no `livestore_runs`, no `my_repo_monitoring` |

### What cron repos add (only this)

1. Log capture on the Python run step (`tee`)
2. **One** `Workflow monitor` step that calls `automationbot-art/github-monitor` — it inserts into the central table automatically

**No other files. No BigQuery scripts. No new tables.**

---

## One-time org secret (not per repo)

| Secret | Where |
| --- | --- |
| `LIVESTORE_SA_JSON` | **automationbot-art** org → Settings → Secrets → Actions |

---

## Rules — do not touch schedule

| Rule | Detail |
| --- | --- |
| **Do NOT change `on:` schedule** | Leave commented `# schedule:` lines as they are |
| **Do NOT uncomment cron** | Manual-only repos stay manual-only |
| **Only add** | Log capture + Workflow monitor step |

---

## Paste block 1 — Update Python run step only

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

- Keep your original step **name** and **python** command
- Add `id: cron`

---

## Paste block 2 — Workflow monitor (writes to central table)

Add **after** the run step, **same job**:

### Manual-only (schedule commented / disabled)

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

### Active cron schedule

Same block — **omit** `schedule-status`.

> Data goes to `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events` — not a repo-local table.

---

## Matrix workflows

Add both blocks **per job**. Use correct `failed-step` per job.

---

## Cursor prompt (paste into each repo)

```
Integrate github-monitor into .github/workflows/ — YAML changes ONLY.

DATA STORAGE (do not get this wrong):
- ALL repos write to ONE table: combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
- Do NOT create BigQuery datasets, tables, or setup scripts in this repo
- Do NOT copy setup_bigquery.py, config/bigquery.json, or insert scripts
- Only add: tee log capture on run step + Workflow monitor step (uses remote action)

SCHEDULE (do not change):
- Leave commented cron and workflow_dispatch exactly as they are
- schedule-status: manual-only if cron is commented/disabled

Monitor action:
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}

No Slack. No new BigQuery resources. Summarize YAML changes only.
```

---

## Verify after first run

In BigQuery console or Looker, query:

```sql
SELECT repository_name, workflow_name, run_date_pkt, dashboard_status, remarks
FROM `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
WHERE repository_name = 'automationbot-art/YOUR_REPO_NAME'
ORDER BY recorded_at DESC
LIMIT 10
```

You should see a new row — **in the shared table**, not a repo-specific table.

---

## Checklist

- [ ] Only `.github/workflows/*.yml` changed
- [ ] No `setup_bigquery.py`, no `config/bigquery.json`, no new BQ tables in this repo
- [ ] Monitor step uses `automationbot-art/github-monitor/.github/actions/workflow-monitor@main`
- [ ] `schedule-status: manual-only` if manual-only repo
- [ ] Row appears in **central** table after test run
