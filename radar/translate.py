"""Translate release titles/summaries into other languages via the LLM.

Each language gets a `site/i18n/{lang}.json` mapping a release's dedup key to
{"title", "summary"}. Incremental and add-only: existing translations are never
re-done or deleted, only missing ones are filled in — so a bad run can't lose
work (same data-safety stance as build_site's floor guard).

Backfill runs locally on free Ollama; CI keeps new releases fresh via the same
dual-mode client (GitHub Models, no API key).
"""
from __future__ import annotations

import json
import os
import re

from .build_site import SITE_DIR, SITE_JSON
from .ollama_client import generate_json

I18N_DIR = SITE_DIR / "i18n"

LANGS = {
    "vi": "Vietnamese",
    "es": "Spanish",
    "zh": "Simplified Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "fr": "French",
}

# Local default: qwen3:4b handles world languages far better than the coder model.
LOCAL_TRANSLATE_MODEL = "qwen3:4b"

_PROMPT = """Translate this AI-news release into {language}.
Rules: keep company names, product/model names, and established technical terms
(API, GPU, token, benchmark names) in English. Natural, concise news style —
no commentary, no romanization.
Return ONLY JSON: {{"title": "...", "summary": "..."}}

Title: {title}
Summary: {summary}"""


def key_for(r: dict) -> str:
    """Mirror Release.dedup_key() for plain dicts from releases.json."""
    product = re.sub(r"[^a-z0-9]+", "", str(r.get("product", "")).lower())
    return f"{str(r.get('company', '')).strip().lower()}|{product}|{r.get('type', '')}"


def _load(lang: str) -> dict:
    path = I18N_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 — corrupt file: start fresh rather than crash
        return {}


def _save(lang: str, data: dict) -> None:
    I18N_DIR.mkdir(parents=True, exist_ok=True)
    (I18N_DIR / f"{lang}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )


def _translate_one(release: dict, language: str) -> dict | None:
    local = not os.environ.get("RADAR_LLM_BASE_URL")
    prompt = _PROMPT.format(
        language=language, title=release["title"], summary=release.get("summary", "")[:900]
    )
    if local:
        prompt = "/no_think\n" + prompt  # qwen3: skip thinking, straight to JSON
    try:
        data = json.loads(generate_json(prompt, model=LOCAL_TRANSLATE_MODEL if local else None))
        title, summary = str(data.get("title", "")).strip(), str(data.get("summary", "")).strip()
        if title and summary:
            return {"title": title, "summary": summary}
    except Exception:  # noqa: BLE001 — one bad item never stops the run
        pass
    return None


def translate_missing(cap: int | None = None) -> int:
    """Fill in missing translations for all languages. Returns calls made.

    `cap` bounds total LLM calls this run (CI quota guard); the rest are picked
    up next run.
    """
    if not SITE_JSON.exists():
        print("translate: no releases.json yet — run build first.")
        return 0
    releases = json.loads(SITE_JSON.read_text(encoding="utf-8")).get("releases", [])
    calls = 0
    for lang, language in LANGS.items():
        done = _load(lang)
        missing = [r for r in releases if key_for(r) not in done]
        if not missing:
            print(f"  {lang}: complete ({len(done)} translated)")
            continue
        print(f"  {lang}: {len(missing)} missing")
        for i, r in enumerate(missing, 1):
            if cap is not None and calls >= cap:
                print(f"  ! translate cap {cap} reached — the rest continue next run")
                _save(lang, done)
                return calls
            tr = _translate_one(r, language)
            calls += 1
            if tr:
                done[key_for(r)] = tr
            if i % 5 == 0 or i == len(missing):
                _save(lang, done)
                print(f"    {lang} {i}/{len(missing)}")
        _save(lang, done)
    return calls
