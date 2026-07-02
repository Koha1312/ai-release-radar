"""Weekly digest: the bot writes a short "This week in AI" recap.

`site/digest.json` = {"week_of", "generated_at", "count", "text": {lang: str}}.
The English recap is LLM-written from the last 7 days of releases, then run
through the same translation pipeline as release content. Regenerated when
older than 6 days (checked during refresh) — fail-soft like everything else.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from .build_site import SITE_JSON, SITE_DIR
from .ollama_client import generate_json
from .translate import LANGS, LOCAL_TRANSLATE_MODEL

DIGEST_JSON = SITE_DIR / "digest.json"

_WRITE = """You are the editor of "AI Release Radar". Write a weekly digest
(3-5 sentences, plain English, factual, no hype) summarizing the most important
AI releases below from the past week. Mention 3-5 standouts by name.
Return ONLY JSON: {{"digest": "..."}}

Releases this week:
{lines}"""

_TRANSLATE = """Translate this weekly AI digest into {language}. Keep company,
product and model names plus established technical terms in English. Natural,
concise news style — no commentary, no romanization.
Return ONLY JSON: {{"digest": "..."}}

Digest: {text}"""


def is_stale() -> bool:
    if not DIGEST_JSON.exists():
        return True
    try:
        d = json.loads(DIGEST_JSON.read_text(encoding="utf-8"))
        age = datetime.now(timezone.utc) - datetime.strptime(
            d["generated_at"], "%Y-%m-%d"
        ).replace(tzinfo=timezone.utc)
        return age.days >= 6
    except Exception:  # noqa: BLE001 — unreadable file counts as stale
        return True


def _gen(prompt: str) -> str:
    local = not os.environ.get("RADAR_LLM_BASE_URL")
    if local:
        prompt = "/no_think\n" + prompt
    raw = generate_json(prompt, model=LOCAL_TRANSLATE_MODEL if local else None)
    return str(json.loads(raw).get("digest", "")).strip()


def build_digest() -> bool:
    """Write digest.json for the past week. Returns True if written."""
    if not SITE_JSON.exists():
        print("digest: no releases.json yet — run build first.")
        return False
    releases = json.loads(SITE_JSON.read_text(encoding="utf-8")).get("releases", [])
    now = datetime.now(timezone.utc)
    week = []
    for r in releases:
        try:
            d = datetime.strptime(r.get("date", ""), "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        if 0 <= (now - d).days <= 7:
            week.append(r)
    if not week:
        print("digest: no releases in the past week — keeping the old digest.")
        return False

    lines = "\n".join(
        f"- {r['company']}: {r['product']} — {r['title']} ({r['type']})" for r in week[:25]
    )
    en = _gen(_WRITE.format(lines=lines))
    if not en:
        print("digest: LLM returned nothing — keeping the old digest.")
        return False

    text = {"en": en}
    for code, language in LANGS.items():
        out = en
        for _attempt in range(3):  # small models sometimes echo English — retry
            try:
                cand = _gen(_TRANSLATE.format(language=language, text=en))
            except Exception:  # noqa: BLE001
                break
            if cand and cand[:60].lower() != en[:60].lower():
                out = cand
                break
        text[code] = out

    DIGEST_JSON.write_text(
        json.dumps(
            {
                "week_of": now.strftime("%Y-%m-%d"),
                "generated_at": now.strftime("%Y-%m-%d"),
                "count": len(week),
                "text": text,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"digest: wrote recap of {len(week)} releases in {len(text)} languages.")
    return True
