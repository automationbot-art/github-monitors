# GitHub Actions Workflow Monitor

Centralized, reusable monitoring for 20+ scheduled Python cron repositories.

## What problem this solves

- **One place to look** instead of scrolling every repo’s Actions tab
- **Slack only on failure** — no noise from successful cron runs
- **Actionable alerts** — repo, failed step, real error text, and recommended fix
- **Persistent summaries** — `media/workflow-summary.md` plus a 30-day `workflow-summary` artifact

This project implements [GitHub Actions Job Summaries](https://github.blog/news-insights/product-news/supercharging-github-actions-with-job-summaries/) (`GITHUB_STEP_SUMMARY`) and extends them with Slack and artifact storage.

## Architecture

```
github-monitors/
├── .github/
│   ├── actions/workflow-monitor/   # Composite action (use in every cron repo)
│   └── workflows/
│       ├── reusable-cron-monitor.yml
│       └── monitor-self-test.yml
├── examples/cron-workflow.yml        # Copy-paste starter for cron repos
├── scripts/                          # Local copies of monitor helpers
└── media/                            # Summary output path (generated at runtime)
```

## Quick start (per cron repository)

### 1. Slack webhook — configure once (organization secret)

**Do not add `SLACK_WEBHOOK_URL` on every cron repo.** Set it once at the org (or user) level; every workflow that references `${{ secrets.SLACK_WEBHOOK_URL }}` will receive it automatically.

#### Create the Slack webhook

1. Slack → **Apps** → create or open your app → **Incoming Webhooks** → On
2. **Add New Webhook to Workspace** → pick a channel (e.g. `#github-cron-alerts`)
3. Copy the webhook URL (`https://hooks.slack.com/services/...`)

#### Store it in one place on GitHub

**Organization (recommended for `automationbot-art` and all cron repos):**

1. GitHub → **automationbot-art** → **Settings** → **Secrets and variables** → **Actions**
2. **New organization secret**
3. Name: `SLACK_WEBHOOK_URL`
4. Value: paste the Slack webhook URL
5. **Repository access:** **All repositories** (or select only repos that run cron workflows)

**Personal account (no org):**

1. GitHub → your profile → **Settings** → **Secrets and variables** → **Actions**
2. **New user secret** with the same name: `SLACK_WEBHOOK_URL`

No per-repo secret is required on `livestore_data_web` or your other cron repos if the org secret is visible to them.

#### Why the webhook cannot live only in `github-monitors`

GitHub Actions secrets are available to the **repository that is running the workflow**. Consumer repos (e.g. `livestore_data_web`) execute the monitor step, so they must have access to `SLACK_WEBHOOK_URL` via an **org/user secret** with that name. The composite action in `automationbot-art/github-monitor` does not hold your webhook; it only receives it as an input.

#### Private `github-monitors` repo

If `automationbot-art/github-monitor` is private, enable org access to private actions:

1. **automationbot-art** → **Settings** → **Actions** → **General**
2. Under **Policies**, allow workflows to use actions from other repos in the org
3. On `github-monitors`: **Settings** → **Actions** → **General** → allow access from org repos (or make the repo public so any repo can `uses:` the action)

### 2. Add the monitor step to your workflow

Copy `examples/cron-workflow.yml` into your cron repo. The action path is `automationbot-art/github-monitor`.

Critical pattern — **pipe logs** so errors are parsed instead of generic exit codes:

```yaml
- name: Run cron job
  id: cron
  run: |
    set -o pipefail
    python main.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"

- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    slack-webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: Run cron job
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
```

### 3. Optional: expose processed record count

In your cron step, write a step output:

```yaml
echo "records-processed=128" >> "$GITHUB_OUTPUT"
```

## What you get on every run

| Output | Location |
| --- | --- |
| Job Summary (UI) | Actions run page → **Summary** tab |
| Markdown file | `media/workflow-summary.md` (during run) |
| Artifact | `workflow-summary` (30-day retention) |
| Slack message | **Only when the workflow fails** |

## Slack message format

```
🚨 GitHub Workflow Failed

Repository:   my-org/my-cron-repo
Workflow:     Daily Cron With Monitor
Failed Step:  Run cron job
Reason:       ValueError: missing BIGQUERY_TABLE env var
Action Required: Add the missing secret or repository variable...
Run URL:      link
Job Summary:  link to artifact
```

## Error detection

The parser prioritizes:

- Python exceptions and tracebacks
- Missing environment variables / secrets
- Authentication failures (401/403)
- Timeouts
- BigQuery errors
- HTTP/API failures
- Shell exit codes (with last log line context)

## Matrix / parallel jobs (e.g. `daily-warehouse.yml`)

When a workflow has **multiple jobs** (rankings × stores, launches × stores), add the monitor block **at the end of each job** that runs Python — not once for the whole workflow.

Each job gets its own:

- `id: cron` on the append/run step (unique per job; same id in different jobs is fine)
- `tee` log capture to `${RUNNER_TEMP}/cron-output.log`
- `Workflow monitor` step with `if: always()`
- `failed-step` matching that job’s step **name** exactly

Example for two jobs:

| Job | `failed-step` value |
| --- | --- |
| `rankings` | `Append rankings` |
| `launches` | `Append new launches + top new free` |

Slack still uses the **same** org secret in every job — you only configure the webhook once.

## Testing this repository

1. Ensure org (or user) secret `SLACK_WEBHOOK_URL` exists — no repo-level copy needed if org access includes this repo
2. Run **Monitor Self Test** workflow
3. Re-run with **Simulate failure** checked to verify Slack + error parsing

## Reusable workflow (two-job pattern)

For repos that prefer a separate monitor job:

```yaml
jobs:
  cron:
    ...
  monitor:
    needs: cron
    if: always()
    uses: automationbot-art/github-monitor/.github/workflows/reusable-cron-monitor.yml@main
    secrets:
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
    with:
      workflow-status: ${{ needs.cron.result }}
      failed-step: Run cron job
```

> Note: the two-job pattern cannot pass runner log files across jobs. Prefer the single-job pattern with `tee` for best error extraction.

## Future extensions

- Microsoft Teams / Discord webhooks (same payload builder pattern)
- Org-level workflow template repository
- Dashboard aggregating artifacts across repos
