"""Export the database to the static site's data file (site/releases.json)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import store

SITE_JSON = Path(__file__).resolve().parent.parent / "site" / "releases.json"


def build() -> int:
    conn = store.connect()
    releases = store.load_all(conn)
    companies = sorted({r["company"] for r in releases})
    types = sorted({r["type"] for r in releases})
    payload = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "count": len(releases),
        "companies": companies,
        "types": types,
        "releases": releases,
    }
    SITE_JSON.parent.mkdir(parents=True, exist_ok=True)
    SITE_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(releases)
