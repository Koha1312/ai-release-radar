"""Fetch raw entries from source feeds. Best-effort: a dead feed is skipped."""
from __future__ import annotations

import feedparser

from .sources import SOURCES


def _fetch_rss(s: dict, limit: int) -> list[dict]:
    feed = feedparser.parse(s["url"])
    if getattr(feed, "bozo", 0) and not feed.entries:
        print(f"  ! {s['name']}: no entries (feed moved?)")
        return []
    out = [{
        "company": s["company"], "source": s["name"],
        "title": e.get("title", ""), "summary": e.get("summary", "")[:1200],
        "url": e.get("link", ""), "published": e.get("published", e.get("updated", "")),
    } for e in feed.entries[:limit]]
    print(f"  + {s['name']}: {len(out)} entries")
    return out


# Adapter registry: source "kind" -> fetcher. Add per-company adapters here.
_ADAPTERS = {"rss": _fetch_rss}


def fetch_raw(limit_per_source: int = 12) -> list[dict]:
    """Return raw items [{company, source, title, summary, url, published}] from all sources."""
    items: list[dict] = []
    for s in SOURCES:
        fetcher = _ADAPTERS.get(s.get("kind", "rss"))
        if not fetcher:
            print(f"  ! {s['name']}: unknown kind '{s.get('kind')}'")
            continue
        try:
            items.extend(fetcher(s, limit_per_source))
        except Exception as exc:  # noqa: BLE001 — never let one bad source kill the run
            print(f"  ! {s['name']}: fetch failed ({exc})")
    return items
