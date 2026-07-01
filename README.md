# github-monitor

Central monitoring for all **private** automationbot-art cron repos.

## Fix `repository not found` (private repos)

**[docs/SECRETS-AND-PRIVATE-REPOS.md](docs/SECRETS-AND-PRIVATE-REPOS.md)** — read this first.

**Quick fix:** make **only** this repo **public** (cron repos stay private). Or enable org Actions access to this private repo.

## Secret (org, once)

| Secret | Value |
| --- | --- |
| **`LIVESTORE_SA_JSON`** | Full service account JSON (`config/livestore.json`) |

Add at **automationbot-art** → Settings → Secrets → Actions → all repos.

## Where data lives

```
combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events
```

## Cron repo integration

- [docs/INTEGRATE-EVERY-REPO.md](docs/INTEGRATE-EVERY-REPO.md)
- [docs/DO-NOT-CREATE-TABLES.md](docs/DO-NOT-CREATE-TABLES.md)

## Repo layout (single copy of code)

| Path | Purpose |
| --- | --- |
| `.github/actions/workflow-monitor/` | Composite action + scripts (used by all cron repos) |
| `config/livestore.json` | Local credentials only (gitignored) |
| `docs/` | All documentation |

No duplicate `scripts/` at repo root — runtime code lives only inside the action folder.
