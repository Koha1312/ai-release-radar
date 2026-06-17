"""Source registry — where we look for new releases.

RSS/Atom feeds are preferred (stable, structured). URLs may need adjusting as
companies move their feeds; a source that fails to fetch is skipped, not fatal.
"""
from __future__ import annotations

SOURCES = [
    {"company": "OpenAI", "name": "OpenAI News", "url": "https://openai.com/news/rss.xml"},
    {"company": "Google", "name": "Google – The Keyword (AI)", "url": "https://blog.google/technology/ai/rss/"},
    {"company": "Google DeepMind", "name": "DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml"},
    {"company": "Microsoft", "name": "Microsoft AI Blog", "url": "https://blogs.microsoft.com/ai/feed/"},
    {"company": "Hugging Face", "name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    # Anthropic has no public RSS at time of writing — add here if/when available.
]
