"""Fetch raw entries from source feeds. Best-effort: a dead feed is skipped."""
from __future__ import annotations

import feedparser

from .sources import SOURCES


def fetch_raw(limit_per_source: int = 12) -> list[dict]:
    """Return raw feed items: [{company, source, title, summary, url, published}]."""
    items: list[dict] = []
    for s in SOURCES:
        try:
            feed = feedparser.parse(s["url"])
        except Exception as exc:  # noqa: BLE001 — never let one bad feed kill the run
            print(f"  ! {s['name']}: fetch failed ({exc})")
            continue
        if getattr(feed, "bozo", 0) and not feed.entries:
            print(f"  ! {s['name']}: no entries (feed moved?)")
            continue
        for e in feed.entries[:limit_per_source]:
            items.append({
                "company": s["company"],
                "source": s["name"],
                "title": e.get("title", ""),
                "summary": e.get("summary", "")[:1200],
                "url": e.get("link", ""),
                "published": e.get("published", e.get("updated", "")),
            })
        print(f"  + {s['name']}: {len(feed.entries[:limit_per_source])} entries")
    return items
