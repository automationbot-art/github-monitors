# Secrets + private repo setup

All your repos are **private**. That is fine — but you must configure access so cron repos can call the `github-monitor` action.

---

## Secrets (Actions)

### One org secret — required for every cron repo

| Secret name | Value | Where to add |
| --- | --- | --- |
| **`LIVESTORE_SA_JSON`** | Full JSON from `config/livestore.json` (entire file, one line) | **automationbot-art** → Settings → Secrets and variables → **Actions** → New organization secret → Repository access: **All repositories** |

No other secrets are required for monitoring (Slack is disabled).

### Optional — only in `github-monitor` repo (not cron repos)

| Secret | When needed |
| --- | --- |
| `LIVESTORE_SA_JSON` | Running **Setup BigQuery Monitoring** or **Monitor Self Test** in this repo (org secret is enough if access includes this repo) |

### Do NOT add per cron repo

- No `SLACK_WEBHOOK_URL`
- No separate GCP keys per repo
- No repo-level copy of `LIVESTORE_SA_JSON` unless org secret cannot cover that repo

---

## Fix: `Unable to resolve action … repository not found`

This error on **private** repos almost always means GitHub cannot **see** `automationbot-art/github-monitor` — not that your YAML is wrong.

### Option A — Make `github-monitor` public (recommended)

Safest and simplest for a **reusable action** repo:

1. Open **automationbot-art/github-monitor** → **Settings** → **General** → Danger zone → **Change visibility** → **Public**
2. The repo contains **no secrets** (only action code). Your cron repos and data stay **private**.
3. Re-run the failed workflow in `livestore_data_web`.

Cron repos keep using:

```yaml
uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
```

### Option B — Keep `github-monitor` private (org configuration)

Do **all** of these:

#### 1. Org Actions policy

**automationbot-art** → **Settings** → **Actions** → **General**

- **Policies** → allow actions from **repositories in this organization**
- Save

#### 2. Allow this repo’s action to be used by other org repos

**automationbot-art/github-monitor** → **Settings** → **Actions** → **General**

- Scroll to **Access**
- Select: **Accessible from repositories in the 'automationbot-art' organization**
- Save

#### 3. Confirm the repo exists and the name is exact

- URL must be: `https://github.com/automationbot-art/github-monitor`
- Not `github-monitors` (with **s**)
- Default branch must be **`main`** (matches `@main` in YAML)

#### 4. Re-run workflow

Actions → failed run → **Re-run all jobs**

If it still fails, use **Option A** (public `github-monitor` only).

---

## Where data is stored (reminder)

**One table for all private cron repos:**

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

Cron repos only **insert rows** via the monitor step. They do not create BigQuery tables.

---

## Checklist

- [ ] Org secret `LIVESTORE_SA_JSON` added with access to all cron repos
- [ ] `github-monitor` is **public** OR private with org Action access enabled
- [ ] Cron workflow uses `automationbot-art/github-monitor/.github/actions/workflow-monitor@main`
- [ ] No per-repo BigQuery setup scripts
- [ ] Re-run workflow after fixing access
