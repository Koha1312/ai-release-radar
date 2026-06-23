"""MCP server — lets an AI assistant query the AI Release Radar live.

Run (stdio):  uv run python -m radar.mcp_server
Then wire it into Claude Code / Claude Desktop (see README). Your assistant can
then answer things like "what open-source models dropped this week?" by calling
these tools against your own radar data.
"""
from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

DATA = Path(__file__).resolve().parent.parent / "site" / "releases.json"

mcp = FastMCP("ai-release-radar")


def _payload() -> dict:
    return json.loads(DATA.read_text(encoding="utf-8"))


@mcp.tool()
def search_releases(
    company: str = "",
    type: str = "",
    open_source: bool | None = None,
    since_days: int = 0,
    query: str = "",
    limit: int = 20,
) -> list[dict]:
    """Search AI releases on the radar (newest first).

    Args:
        company: exact company name, e.g. "OpenAI" (case-insensitive). "" = any.
        type: model | feature | api | platform | deprecation | research. "" = any.
        open_source: True for open-weight only, False for proprietary only, omit for both.
        since_days: only releases from the last N days (0 = no date filter).
        query: free-text match over company/product/title/summary/tags.
        limit: max results (default 20).
    """
    releases = _payload().get("releases", [])
    today = datetime.now(timezone.utc).date()
    out = []
    for r in releases:
        if company and r["company"].lower() != company.lower():
            continue
        if type and r["type"] != type.lower():
            continue
        if open_source is not None and bool(r.get("open_source")) != open_source:
            continue
        if since_days:
            try:
                d = datetime.strptime(r["date"], "%Y-%m-%d").date()
            except (ValueError, KeyError):
                continue
            if (today - d).days > since_days:
                continue
        if query:
            hay = f"{r['company']} {r['product']} {r['title']} {r['summary']} {' '.join(r.get('tags', []))}".lower()
            if query.lower() not in hay:
                continue
        out.append(r)
    return out[:limit]


@mcp.tool()
def list_companies() -> dict:
    """Every tracked company with its number of releases."""
    releases = _payload().get("releases", [])
    return dict(Counter(r["company"] for r in releases).most_common())


@mcp.tool()
def radar_stats() -> dict:
    """Overall radar stats: totals, open-source count, and last update time."""
    data = _payload()
    releases = data.get("releases", [])
    return {
        "total_releases": len(releases),
        "companies": len({r["company"] for r in releases}),
        "open_source": sum(1 for r in releases if r.get("open_source")),
        "updated": data.get("generated_at"),
        "url": "https://koha1312.github.io/ai-release-radar/",
    }


if __name__ == "__main__":
    mcp.run()
