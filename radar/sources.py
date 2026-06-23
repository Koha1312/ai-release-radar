"""Source registry — where we look for new releases.

RSS/Atom feeds are preferred (stable, structured). URLs may need adjusting as
companies move their feeds; a source that fails to fetch is skipped, not fatal.
"""
from __future__ import annotations

SOURCES = [
    {"company": "OpenAI", "name": "OpenAI News", "url": "https://openai.com/news/rss.xml"},
    {"company": "Google", "name": "Google – The Keyword (AI)", "url": "https://blog.google/technology/ai/rss/"},
    {"company": "Google DeepMind", "name": "DeepMind Blog", "url": "https://deepmind.google/blog/rss.xml"},
    {"company": "Microsoft", "name": "Microsoft Blog", "url": "https://blogs.microsoft.com/feed/"},
    {"company": "Hugging Face", "name": "Hugging Face Blog", "url": "https://huggingface.co/blog/feed.xml"},
    {"company": "Mistral", "name": "Mistral AI News", "url": "https://mistral.ai/feed.xml"},
    {"company": "xAI", "name": "xAI News", "url": "https://x.ai/news/rss.xml"},
    {"company": "Stability AI", "name": "Stability AI News", "url": "https://stability.ai/news?format=rss"},
    # Anthropic has no public RSS at time of writing — add here if/when available.
]
