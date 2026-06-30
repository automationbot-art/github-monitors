#!/usr/bin/env python3
"""Insert a workflow monitoring row into BigQuery."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.cloud import bigquery
from google.oauth2 import service_account


def load_config(config_path: Path) -> dict:
    return json.loads(config_path.read_text(encoding="utf-8"))


def get_client(credentials_path: Path, project_id: str) -> bigquery.Client:
    credentials = service_account.Credentials.from_service_account_file(
        str(credentials_path),
        scopes=["https://www.googleapis.com/auth/bigquery"],
    )
    return bigquery.Client(credentials=credentials, project=project_id)


def main() -> int:
    parser = argparse.ArgumentParser(description="Insert workflow run event into BigQuery.")
    parser.add_argument("--row-json", type=Path, required=True, help="JSON file with row fields")
    parser.add_argument("--config", type=Path, default=Path("config/bigquery.json"))
    parser.add_argument("--credentials", type=Path, default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    credentials_path = args.credentials or Path(cfg["credentials_file"])
    project_id = cfg["project_id"]
    table_id = f"{project_id}.{cfg['dataset_id']}.{cfg['table_id']}"

    row = json.loads(args.row_json.read_text(encoding="utf-8"))
    client = get_client(credentials_path, project_id)

    errors = client.insert_rows_json(table_id, [row])
    if errors:
        print(json.dumps(errors, indent=2), file=sys.stderr)
        return 1

    print(f"Inserted event_id={row.get('event_id')} into {table_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
