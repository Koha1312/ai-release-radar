"""Turn a raw feed item into a structured Release via the local LLM.

The model does two jobs: (1) decide whether the item is actually an AI release
worth tracking (vs. company PR, hiring posts, etc.), and (2) if so, normalize it
into our schema. Anything it isn't sure about is dropped — we'd rather miss a
release than pollute the tracker with noise.
"""
from __future__ import annotations

import json

from pydantic import ValidationError

from .ollama_client import generate_json
from .schema import Release

_PROMPT = """You normalize tech-news items into a strict JSON schema for an AI-release tracker.

Decide if this item is a concrete AI RELEASE worth tracking: a new model, API, feature,
platform, research artifact, or a deprecation/retirement. Marketing, hiring, opinion,
or event recaps with no concrete release => not a release.

Return ONLY JSON:
{{"is_release": true/false,
  "product": "short model/product name",
  "title": "concise headline",
  "summary": "1-2 sentence plain-English summary",
  "date": "YYYY-MM-DD",
  "type": "model|feature|api|platform|deprecation|research",
  "tags": ["short","tags"]}}

Company: {company}
Published: {published}
Title: {title}
Body: {summary}
"""


def extract_release(item: dict) -> Release | None:
    raw = generate_json(_PROMPT.format(
        company=item["company"], published=item.get("published", ""),
        title=item["title"], summary=item.get("summary", ""),
    ))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not data.get("is_release"):
        return None
    try:
        return Release(
            company=item["company"],
            product=data.get("product") or item["title"][:60],
            title=data.get("title") or item["title"],
            summary=data.get("summary", ""),
            date=data.get("date") or "",
            type=data.get("type", "feature"),
            url=item.get("url", ""),
            tags=data.get("tags", []) or [],
        )
    except ValidationError:
        return None


def extract_many(items: list[dict]) -> list[Release]:
    out: list[Release] = []
    for i, item in enumerate(items, 1):
        print(f"  extracting {i}/{len(items)}: {item['title'][:55]}")
        rel = extract_release(item)
        if rel and rel.date:
            out.append(rel)
    return out
