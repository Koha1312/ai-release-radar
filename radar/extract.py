"""Turn a raw feed item into a structured Release via the local LLM.

The model does two jobs: (1) decide whether the item is actually an AI release
worth tracking (vs. company PR, hiring posts, etc.), and (2) if so, normalize it
into our schema. Anything it isn't sure about is dropped — we'd rather miss a
release than pollute the tracker with noise.
"""
from __future__ import annotations

import json
import re

from pydantic import ValidationError

from .ollama_client import generate_json
from .schema import Release

# Prompt-injection defense: a feed item containing these is untrusted manipulation,
# not a real release — skip it before it ever reaches the LLM.
_INJECTION = re.compile(
    r"ignore (all|any|the|previous|prior|above)|disregard (the|all|previous|above|your)"
    r"|system prompt|you are now|new instructions|mark (all|everything)|jailbreak"
    r"|prompt inject|override (the|your|all)",
    re.IGNORECASE,
)


def looks_injected(item: dict) -> bool:
    return bool(_INJECTION.search(f"{item.get('title', '')} {item.get('summary', '')}"))

_PROMPT = """You normalize tech-news items into a strict JSON schema for an AI-release tracker.

Decide if this item announces a concrete AI RELEASE BY THIS COMPANY worth tracking:
a NAMED new model, API, developer feature, platform/tool, or a deprecation/retirement.

Set is_release=FALSE for: customer/case studies ("how <someone> uses AI"), acquisitions,
partnerships, funding, hiring, policy/safety/opinion essays, event recaps, and research
write-ups with no named shipped artifact. The "product" must be the company's OWN named
model/product — never a customer's name. When in doubt, choose false.

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
    try:
        raw = generate_json(_PROMPT.format(
            company=item["company"], published=item.get("published", ""),
            title=item["title"], summary=item.get("summary", ""),
        ))
        data = json.loads(raw)
    except Exception:  # noqa: BLE001 — network/LLM/JSON error: skip this item, keep going
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


_VERIFY_PROMPT = """A first pass extracted the item below as an AI release. Verify STRICTLY.
Return ONLY JSON: {{"keep": true}} or {{"keep": false}}.

keep=true ONLY if this is a real, concrete, AI/ML-related release BY {company} — a named
model, AI feature, AI API, AI platform, or AI-product deprecation.
keep=false for: anything NOT about AI/ML (generic DevOps, dependency/billing/security/UI
changes with no AI angle), customer/case studies, acquisitions, partnerships, funding,
hiring, opinion/policy essays, event recaps, research write-ups with no named shipped
artifact, or if the product is not {company}'s own.

Company: {company}
Extracted product: {product}
Title: {title}
Summary: {summary}"""


def verify_release(rel: Release) -> bool:
    """Second-pass check: a separate LLM call confirms this is a real release.

    Fails open (keeps) on any error — a transient verifier failure shouldn't drop
    a genuine release the first pass already accepted.
    """
    try:
        raw = generate_json(_VERIFY_PROMPT.format(
            company=rel.company, product=rel.product, title=rel.title, summary=rel.summary[:600],
        ))
        return bool(json.loads(raw).get("keep", True))
    except Exception:  # noqa: BLE001
        return True


def extract_many(items: list[dict]) -> list[Release]:
    """Extract (bot 1) then verify (bot 2) each item; only verified releases pass."""
    out: list[Release] = []
    for i, item in enumerate(items, 1):
        if looks_injected(item):
            print(f"    ! injection guard: blocked {item.get('source', '?')} / {item['title'][:45]}")
            continue
        print(f"  extracting {i}/{len(items)}: {item['title'][:55]}")
        rel = extract_release(item)
        if not (rel and rel.date):
            continue
        if not verify_release(rel):
            print(f"    x verifier dropped: {rel.company} / {rel.product}")
            continue
        out.append(rel)
    return out
