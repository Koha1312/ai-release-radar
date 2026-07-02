"""Source registry — where we look for new releases.

RSS/Atom feeds are preferred (stable, structured). URLs may need adjusting as
companies move their feeds; a source that fails to fetch is skipped, not fatal.
"""
from __future__ import annotations

# Each source has a `kind` (the adapter to fetch it with). "rss" is the default;
# the structure lets us add per-company adapters (json APIs, etc.) without
# touching the rest of the pipeline.
SOURCES = [
    {"company": "OpenAI", "name": "OpenAI News", "kind": "rss", "url": "https://openai.com/news/rss.xml"},
    {"company": "Google", "name": "Google – The Keyword (AI)", "kind": "rss", "url": "https://blog.google/technology/ai/rss/"},
    {"company": "Google DeepMind", "name": "DeepMind Blog", "kind": "rss", "url": "https://deepmind.google/blog/rss.xml"},
    {"company": "Microsoft", "name": "Microsoft Blog", "kind": "rss", "url": "https://blogs.microsoft.com/feed/"},
    {"company": "GitHub", "name": "GitHub Changelog", "kind": "rss", "url": "https://github.blog/changelog/feed/"},
    {"company": "Hugging Face", "name": "Hugging Face Blog", "kind": "rss", "url": "https://huggingface.co/blog/feed.xml"},
    {"company": "Mistral", "name": "Mistral AI News", "kind": "rss", "url": "https://mistral.ai/rss.xml"},
    {"company": "Brave", "name": "Brave Blog", "kind": "rss", "url": "https://brave.com/blog/index.xml"},
    # Tools without RSS but with public GitHub releases (keyless API; the
    # adapter keeps only majors/minors so patch releases never reach the LLM).
    {"company": "Zed", "name": "Zed Releases", "kind": "github_releases", "repo": "zed-industries/zed"},
    {"company": "n8n", "name": "n8n Releases", "kind": "github_releases", "repo": "n8n-io/n8n"},
    {"company": "Ollama", "name": "Ollama Releases", "kind": "github_releases", "repo": "ollama/ollama"},
    {"company": "vLLM", "name": "vLLM Releases", "kind": "github_releases", "repo": "vllm-project/vllm"},
    # No working public RSS found for xAI (Cloudflare-blocked), Stability AI,
    # Anthropic, ElevenLabs, Cursor, Raycast or Perplexity (checked 2026-07-02) —
    # they stay tracked via curated entries.
]
