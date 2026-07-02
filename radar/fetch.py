"""Fetch raw entries from source feeds. Best-effort: a dead feed is skipped."""
from __future__ import annotations

import json
import os
import re
import urllib.request

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


# Only feed the LLM meaningful versions: x.y.0 majors/minors, not every patch.
_PATCH_RE = re.compile(r"\d+\.\d+\.(\d+)")


def _is_patch_release(tag: str) -> bool:
    m = _PATCH_RE.search(tag or "")
    return bool(m and m.group(1) != "0")


def _fetch_github_releases(s: dict, limit: int) -> list[dict]:
    """GitHub Releases API — keyless for public repos; token used if available.

    Skips drafts, prereleases and patch releases (x.y.Z with Z>0) so only
    releases that might actually matter reach the LLM.
    """
    headers = {"User-Agent": "ai-release-radar", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GH_API_TOKEN", "")
    if token:  # CI: raises the rate limit; locally unauthenticated is plenty
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"https://api.github.com/repos/{s['repo']}/releases?per_page={limit}", headers=headers
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        releases = json.loads(r.read())
    out = []
    for rel in releases:
        if rel.get("draft") or rel.get("prerelease") or _is_patch_release(rel.get("tag_name", "")):
            continue
        out.append({
            "company": s["company"], "source": s["name"],
            "title": f"{s['company']} {rel.get('name') or rel.get('tag_name', '')}".strip(),
            "summary": (rel.get("body") or "")[:1200],
            "url": rel.get("html_url", ""),
            "published": rel.get("published_at", ""),
        })
    print(f"  + {s['name']}: {len(out)} entries (majors/minors only)")
    return out


# Adapter registry: source "kind" -> fetcher. Add per-company adapters here.
_ADAPTERS = {"rss": _fetch_rss, "github_releases": _fetch_github_releases}


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
