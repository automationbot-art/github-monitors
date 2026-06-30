---
name: github-workflow-monitor
description: Integrate the automationbot-art/github-monitor composite action into cron workflow YAML files. Use when adding BigQuery monitoring, job summaries, or rolling out the monitor across repositories.
---

# GitHub Workflow Monitor Integration

## When to use

- Adding monitoring to a scheduled/cron GitHub Actions workflow
- Rolling out `workflow-monitor` across multiple repositories
- Updating consumer repos after monitor action API changes

## Action reference

```
automationbot-art/github-monitor/.github/actions/workflow-monitor@main
```

## Required org secret

| Secret | Value |
| --- | --- |
| `LIVESTORE_SA_JSON` | Full GCP service account JSON (same as `config/livestore.json`) |

## Integration pattern

### Change 1 — Run step (log capture)

```yaml
- name: <keep original step name>
  id: cron
  run: |
    set -o pipefail
    python your_script.py 2>&1 | tee "${RUNNER_TEMP}/cron-output.log"
    ROWS="$(grep -oE 'rows~=[0-9]+' "${RUNNER_TEMP}/cron-output.log" | tail -1 | cut -d= -f2 || true)"
    echo "records-processed=${ROWS:-0}" >> "$GITHUB_OUTPUT"
```

### Change 2 — Monitor step (after run step, same job)

```yaml
- name: Workflow monitor
  if: always()
  uses: automationbot-art/github-monitor/.github/actions/workflow-monitor@main
  with:
    gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}
    workflow-status: ${{ steps.cron.outcome }}
    failed-step: <exact run step name>
    log-file: ${{ runner.temp }}/cron-output.log
    records-processed: ${{ steps.cron.outputs.records-processed }}
```

## Matrix workflows

Add both changes **per job** (rankings, launches, etc.). `id: cron` can repeat across separate jobs.

## Do not change

- Schedule/cron triggers
- Matrix dimensions
- Unrelated setup steps

## Slack

Slack notifications are **disabled** in the action. Do not add `SLACK_WEBHOOK_URL` unless re-enabling commented steps in the action.
