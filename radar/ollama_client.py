"""Tiny Ollama REST client (stdlib only) for local structuring of feed items."""
from __future__ import annotations

import json
import urllib.request

OLLAMA = "http://localhost:11434"
MODEL = "qwen2.5-coder:7b"  # reliable JSON output


def generate_json(prompt: str, model: str = MODEL) -> str:
    """Ask the local model for a JSON response (format=json forces valid JSON)."""
    payload = {"model": model, "prompt": prompt, "stream": False, "format": "json", "think": False}
    req = urllib.request.Request(
        OLLAMA + "/api/generate",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"]
