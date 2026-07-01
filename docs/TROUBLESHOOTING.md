# Troubleshooting

## `Unexpected input(s) 'gcp-credentials-json'`

**Cause:** Workflow YAML still uses the old input name.

**Fix** in `livestore_data_web` (and every cron repo):

```yaml
# Wrong
gcp-credentials-json: ${{ secrets.LIVESTORE_SA_JSON }}

# Correct
gcp-credentials-base64: ${{ secrets.LIVESTORE_SA_BASE64 }}
```

Secret name must be **`LIVESTORE_SA_BASE64`** (base64-encoded `livestore.json`).

---

## `JSONDecodeError: Expecting value: line 1 column 1`

**Cause:** Almost always the same as above — `gcp-credentials-base64` was **empty** because YAML still passed `gcp-credentials-json`, which the action ignores.

**Fix:**
1. Update monitor step input to `gcp-credentials-base64`
2. Add repository secret **`LIVESTORE_SA_BASE64`** on **livestore_data_web**
3. Re-run workflow

---

## `Unable to resolve action … repository not found`

**Cause:** Wrong repo name or private action without access.

**Fix:** Use exact path:

```yaml
uses: automationbot-art/github-monitors/.github/actions/workflow-monitor@main
```

Not `github-monitor` (no **s**). Repo must be **public** or org must allow private action access.

---

## Job summary works but BigQuery step fails

Summary and artifact run **before** BigQuery insert. A successful summary does **not** mean BigQuery succeeded.

Check the **Write GCP credentials** and **Insert workflow run into BigQuery** steps in the log.

---

## Verify secret encoding (PowerShell)

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("config\livestore.json"))
```

Paste output as `LIVESTORE_SA_BASE64` on the **same repo** that runs the workflow.
