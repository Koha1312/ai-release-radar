"""SQLite store. The single place that touches the database.

Dedup is enforced by a UNIQUE `dedup_key` so the same release reported by
several sources (or re-ingested daily) updates in place instead of piling up.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .schema import Release

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "radar.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS releases (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    dedup_key  TEXT UNIQUE NOT NULL,
    company    TEXT NOT NULL,
    product    TEXT NOT NULL,
    title      TEXT NOT NULL,
    summary    TEXT NOT NULL,
    date       TEXT NOT NULL,
    type       TEXT NOT NULL,
    url        TEXT,
    tags       TEXT,
    open_source INTEGER NOT NULL DEFAULT 0,
    image      TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_releases_date ON releases(date);
CREATE INDEX IF NOT EXISTS idx_releases_company ON releases(company);
"""


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    return conn


def upsert(conn: sqlite3.Connection, r: Release) -> None:
    conn.execute(
        """
        INSERT INTO releases (dedup_key, company, product, title, summary, date, type, url, tags, open_source, image)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(dedup_key) DO UPDATE SET
            company=excluded.company, product=excluded.product, title=excluded.title,
            summary=excluded.summary, date=excluded.date, type=excluded.type,
            url=excluded.url, tags=excluded.tags, open_source=excluded.open_source,
            image=excluded.image
        """,
        (
            r.dedup_key(), r.company, r.product, r.title, r.summary,
            r.date, r.type.value, r.url, json.dumps(r.tags), int(r.open_source), r.image,
        ),
    )
    conn.commit()


def upsert_many(conn: sqlite3.Connection, releases: list[Release]) -> int:
    for r in releases:
        upsert(conn, r)
    return len(releases)


def load_all(conn: sqlite3.Connection) -> list[dict]:
    """All releases, newest first, as plain dicts ready for JSON."""
    rows = conn.execute(
        "SELECT company, product, title, summary, date, type, url, tags, open_source, image "
        "FROM releases ORDER BY date DESC, id DESC"
    ).fetchall()
    out = []
    for row in rows:
        d = dict(row)
        d["tags"] = json.loads(d["tags"]) if d["tags"] else []
        d["open_source"] = bool(d["open_source"])
        out.append(d)
    return out
