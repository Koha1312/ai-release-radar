"""LLM client for structuring feed items.

Works two ways with no code change:
- **Local** (default): talks to Ollama at localhost (your machine).
- **Cloud** (CI): if RADAR_LLM_BASE_URL is set, talks to any OpenAI-compatible
  endpoint — e.g. GitHub Models (free in Actions via GITHUB_TOKEN), Groq, etc.
"""
from __future__ import annotations

import json
import os
import urllib.request

OLLAMA = "http://localhost:11434"
LOCAL_MODEL = "qwen2.5-coder:7b"  # local default


def _post(url: str, payload: dict, headers: dict | None = None) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())


def generate_json(prompt: str, model: str | None = None) -> str:
    """Return a JSON string from the model (cloud if configured, else local Ollama)."""
    base = os.environ.get("RADAR_LLM_BASE_URL", "").rstrip("/")
    if base:
        # OpenAI-compatible chat completions (GitHub Models / Groq / OpenRouter / …)
        resp = _post(
            base + "/chat/completions",
            {
                "model": model or os.environ.get("RADAR_LLM_MODEL", "openai/gpt-4o-mini"),
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "temperature": 0,
            },
            {"Authorization": f"Bearer {os.environ.get('RADAR_LLM_API_KEY', '')}"},
        )
        return resp["choices"][0]["message"]["content"]

    # Local Ollama (format=json forces valid JSON)
    resp = _post(
        OLLAMA + "/api/generate",
        {"model": model or LOCAL_MODEL, "prompt": prompt, "stream": False,
         "format": "json", "think": False},
    )
    return resp["response"]
