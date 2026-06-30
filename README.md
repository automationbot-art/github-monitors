# github-monitor

Reusable GitHub Actions monitoring for scheduled cron workflows across many repositories.

**Repo:** [automationbot-art/github-monitor](https://github.com/automationbot-art/github-monitor)

**Slack alerts on failure only** · **Job Summaries** · **`media/workflow-summary.md`** · **30-day artifacts**

## Documentation

See [docs/setup.md](docs/setup.md) for full setup, **org-level Slack webhook** (one secret for all repos), and per-repo integration.

## Components

| Component | Purpose |
| --- | --- |
| `.github/actions/workflow-monitor` | Composite action — summary, artifact, Slack |
| `.github/workflows/reusable-cron-monitor.yml` | Callable reusable workflow |
| `examples/cron-workflow.yml` | Starter workflow for cron repos |
| `scripts/` | Error parser and Markdown summary generators |

## License

MIT
