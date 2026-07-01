# Setup (github-monitors repo only)

## 1. Org secret

| Secret | Where |
| --- | --- |
| `LIVESTORE_SA_BASE64` | automationbot-art org → Actions secrets → all repos (base64-encoded SA JSON) |

## 2. Private repo access

Cron repos must resolve `automationbot-art/github-monitors`. See [SECRETS-AND-PRIVATE-REPOS.md](SECRETS-AND-PRIVATE-REPOS.md).

## 3. Provision BigQuery (this repo only)

```bash
pip install -r requirements.txt
python .github/actions/workflow-monitor/scripts/setup_bigquery.py \
  --config .github/actions/workflow-monitor/config/bigquery.json \
  --credentials config/livestore.json
```

Or run workflow **Setup BigQuery Monitoring**.

## 4. Integrate cron repos

[INTEGRATE-EVERY-REPO.md](INTEGRATE-EVERY-REPO.md)

## Central table

`combine-data-pipeline-482809.github_cron_monitoring.workflow_run_events`
