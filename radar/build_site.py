"""Export the database to the static site's data files (releases.json + rss.xml)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import store

SITE_DIR = Path(__file__).resolve().parent.parent / "site"
SITE_JSON = SITE_DIR / "releases.json"
SITE_RSS = SITE_DIR / "rss.xml"
SITE_URL = "https://koha1312.github.io/ai-release-radar/"


def _xml_escape(s: str) -> str:
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;").replace("'", "&apos;")
    )


def _rfc822(date: str) -> str:
    try:
        return datetime.strptime(date, "%Y-%m-%d").strftime("%a, %d %b %Y 00:00:00 +0000")
    except (ValueError, TypeError):
        return ""


def _build_rss(releases: list[dict], generated_at: str) -> None:
    items = []
    for r in releases:
        link = r.get("url") or SITE_URL
        desc = f"[{r['company']}] {r['summary']}"
        pub = _rfc822(r.get("date", ""))
        items.append(
            "    <item>\n"
            f"      <title>{_xml_escape(r['product'])} — {_xml_escape(r['title'])}</title>\n"
            f"      <link>{_xml_escape(link)}</link>\n"
            f"      <guid isPermaLink=\"false\">{_xml_escape(r['company'] + '|' + r['product'] + '|' + r['type'])}</guid>\n"
            f"      <category>{_xml_escape(r['company'])}</category>\n"
            + (f"      <pubDate>{pub}</pubDate>\n" if pub else "")
            + f"      <description>{_xml_escape(desc)}</description>\n"
            "    </item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n  <channel>\n'
        "    <title>AI Release Radar</title>\n"
        f"    <link>{SITE_URL}</link>\n"
        "    <description>Every AI release worth knowing — from the big labs to the tools we use.</description>\n"
        f"    <lastBuildDate>{generated_at}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    SITE_RSS.write_text(rss, encoding="utf-8")


def build() -> int:
    conn = store.connect()
    releases = store.load_all(conn)
    companies = sorted({r["company"] for r in releases})
    types = sorted({r["type"] for r in releases})
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    payload = {
        "generated_at": generated_at,
        "count": len(releases),
        "companies": companies,
        "types": types,
        "releases": releases,
    }
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    SITE_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    _build_rss(releases, datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000"))
    return len(releases)
