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
    # No working public RSS found for xAI (Cloudflare-blocked) or Stability AI —
    # they stay tracked via curated entries. Anthropic also has no public RSS yet.
]
