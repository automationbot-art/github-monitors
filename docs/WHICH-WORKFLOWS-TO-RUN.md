# Which GitHub Actions to run (and where)

Repo name on GitHub: **`automationbot-art/github-monitors`** (with **s**).

Correct action path in cron YAML:

```yaml
uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
```

---

## Before anything: org secret

| Secret | Where |
| --- | --- |
| `LIVESTORE_SA_BASE64` | **automationbot-art** org → Settings → Secrets → Actions → all repos |

---

## Run order

### Step 1 — `github-monitors` repo (this repo, now public)

| Workflow | When | Purpose |
| --- | --- | --- |
| **Setup BigQuery Monitoring** | **Once** (skip if already ran) | Creates dataset + table |
| **Monitor Self Test** | Optional sanity check | Tests summary + BigQuery insert |

**Actions** → **Setup BigQuery Monitoring** → **Run workflow**

Then optionally: **Monitor Self Test** → Run workflow (toggle simulate failure to test errors).

### Step 2 — `livestore_data_web` (your private cron repo)

| Workflow | When | Purpose |
| --- | --- | --- |
| **daily-warehouse** (or your workflow name) | Every real run | Runs ETL + writes row to central BigQuery table |

**First:** fix YAML if it still says `github-monitor` (no **s**):

```yaml
uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
```

**Then:** Actions → **daily-warehouse.yml** → **Run workflow** (manual trigger).

This is the workflow that matters for production data.

---

## Summary

| Repo | Run this | Why |
| --- | --- | --- |
| **github-monitors** | Setup BigQuery (once) + Self Test (optional) | Infrastructure + smoke test |
| **livestore_data_web** | **daily-warehouse** (your cron) | Real monitoring data for Looker |

---

## Verify data landed

```sql
SELECT repository_name, workflow_name, run_date_pkt, dashboard_status, remarks
FROM `combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
WHERE repository_name = 'automationbot-art/livestore_data_web'
ORDER BY recorded_at DESC
LIMIT 10
```

---

## If livestore still fails on the monitor step

1. Confirm `uses:` line says **`github-monitors`** (with **s**)
2. Confirm `github-monitors` repo is **public** on `main` branch
3. Confirm org secret `LIVESTORE_SA_BASE64` exists
4. Re-run workflow
