"""Export the database to the static site's data files (releases.json + rss.xml)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from . import store

# A release is "official" when its source URL is the company's own domain
# (a primary announcement) rather than a secondary news site (reported).
_OFFICIAL_DOMAINS = {
    "Anthropic": ["anthropic.com"],
    "OpenAI": ["openai.com"],
    "Google": ["google.com", "blog.google", "deepmind.google", "ai.google.dev", "googleblog.com"],
    "Google DeepMind": ["deepmind.google", "blog.google", "google.com"],
    "Microsoft": ["microsoft.com"],
    "Meta": ["meta.com", "fb.com", "facebook.com"],
    "Z.ai": ["z.ai", "zhipuai.cn", "bigmodel.cn"],
    "DeepSeek": ["deepseek.com"],
    "Moonshot AI": ["moonshot.ai", "moonshot.cn", "moonshotai.github.io", "github.com"],
    "ElevenLabs": ["elevenlabs.io"],
    "GitHub": ["github.com", "github.blog"],
    "Apple": ["apple.com"],
    "OpenClaw": ["getopenclaw.ai", "openclaw.ai", "github.com"],
    "n8n": ["n8n.io", "github.com"],
    "Notion": ["notion.com", "notion.so"],
    "Raycast": ["raycast.com"],
    "Zed": ["zed.dev", "github.com"],
    "Ollama": ["ollama.com", "github.com"],
    "vLLM": ["vllm.ai", "github.com"],
    "Canva": ["canva.com"],
    "Figma": ["figma.com"],
    "Brave": ["brave.com"],
    "Perplexity": ["perplexity.ai"],
    "Cursor": ["cursor.com", "cursor.sh"],
    "Obsidian": ["obsidian.md"],
    "xAI": ["x.ai"],
}


def _is_official(company: str, url: str) -> bool:
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return any(host == d or host.endswith("." + d) for d in _OFFICIAL_DOMAINS.get(company, []))

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
        '<?xml-stylesheet type="text/xsl" href="rss.xsl"?>\n'
        '<rss version="2.0">\n  <channel>\n'
        "    <title>AI Release Radar</title>\n"
        f"    <link>{SITE_URL}</link>\n"
        "    <description>Every AI release worth knowing — from the big labs to the tools we use.</description>\n"
        f"    <lastBuildDate>{generated_at}</lastBuildDate>\n"
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )
    SITE_RSS.write_text(rss, encoding="utf-8")


_PERSIST_KEYS = ("company", "product", "title", "summary", "date", "type", "url", "tags", "open_source", "image")


def load_existing(conn) -> int:
    """Upsert releases from a previously-built releases.json into the DB.

    The DB is ephemeral in CI, but releases.json is committed — so loading it
    back makes past auto-discovered releases persist across runs.
    """
    from .schema import Release  # local import avoids a cycle at module load

    if not SITE_JSON.exists():
        return 0
    data = json.loads(SITE_JSON.read_text(encoding="utf-8"))
    n = 0
    for d in data.get("releases", []):
        try:
            store.upsert(conn, Release(**{k: d[k] for k in _PERSIST_KEYS if k in d}))
            n += 1
        except Exception:  # noqa: BLE001 — skip a malformed record, keep the rest
            continue
    return n


# Safety floor: the curated baseline alone is ~108 releases, so anything well
# below this means something broke (seed didn't load, DB corrupt). Refuse to
# overwrite the live site data with a suspiciously-small set.
FLOOR = 100


def build() -> int:
    conn = store.connect()
    releases = store.load_all(conn)
    if len(releases) < FLOOR:
        raise SystemExit(
            f"ABORT build: only {len(releases)} releases (< floor {FLOOR}). "
            "Refusing to overwrite site data — possible corruption/data loss."
        )
    for r in releases:
        r["official"] = _is_official(r["company"], r.get("url", ""))
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
