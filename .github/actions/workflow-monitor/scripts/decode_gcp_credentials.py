#!/usr/bin/env python3
"""Decode LIVESTORE_SA_BASE64 and write a GCP service account JSON file."""

from __future__ import annotations

import base64
import json
import os
import sys


def main() -> int:
    creds_file = os.environ["CREDS_FILE"]
    raw_b64 = os.environ.get("GCP_CREDENTIALS_BASE64", "").strip()

    if not raw_b64:
        print(
            "::error::gcp-credentials-base64 is empty.\n"
            "Fix workflow YAML:\n"
            "  gcp-credentials-base64: ${{ secrets.LIVESTORE_SA_BASE64 }}\n"
            "Remove gcp-credentials-json (old input name). Add LIVESTORE_SA_BASE64 secret on this repo.",
            file=sys.stderr,
        )
        return 1

    # Remove whitespace/newlines often introduced when pasting base64.
    compact = "".join(raw_b64.split())

    try:
        decoded = base64.b64decode(compact, validate=False)
    except Exception as exc:
        print(f"::error::LIVESTORE_SA_BASE64 is not valid base64: {exc}", file=sys.stderr)
        return 1

    if not decoded.strip():
        print("::error::LIVESTORE_SA_BASE64 decoded to empty content.", file=sys.stderr)
        return 1

    try:
        json.loads(decoded.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(
            f"::error::Decoded secret is not valid service account JSON: {exc}\n"
            "Re-encode config/livestore.json: "
            "[Convert]::ToBase64String([IO.File]::ReadAllBytes('config\\livestore.json'))",
            file=sys.stderr,
        )
        return 1

    with open(creds_file, "wb") as handle:
        handle.write(decoded)

    print(f"Wrote GCP credentials to {creds_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
