"""The one canonical shape of an AI release record.

Everything in the pipeline (seed data, LLM extraction, the site JSON) conforms
to this, so the frontend never has to guess.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ReleaseType(str, Enum):
    MODEL = "model"            # a new model / version
    FEATURE = "feature"        # a product feature
    API = "api"               # API / developer-platform change
    PLATFORM = "platform"      # infra / platform / tooling
    DEPRECATION = "deprecation"  # retirement / sunset / suspension
    RESEARCH = "research"      # paper / research release


class Release(BaseModel):
    company: str = Field(description="e.g. 'Anthropic', 'OpenAI', 'Google', 'Microsoft'")
    product: str = Field(description="Short product/model name, e.g. 'Claude Opus 4.8'")
    title: str = Field(description="Headline of the release")
    summary: str = Field(description="1-2 sentence plain-English summary")
    date: str = Field(description="Release date, ISO format YYYY-MM-DD")
    type: ReleaseType
    url: str = Field(default="", description="Source link")
    tags: list[str] = Field(default_factory=list)

    def dedup_key(self) -> str:
        """Stable identity of a release EVENT: company + product + type.

        Not the URL — several distinct releases are often announced in one
        article (so they'd share a URL), while the same release from different
        sources has different URLs. (company, product, type) collapses re-ingests
        of the same event without merging genuinely different ones. Cross-source
        name-variant matching ("GPT-5.5" vs "GPT 5.5") is a future entity-resolution step.
        """
        return f"{self.company}|{self.product}|{self.type.value}".strip().lower()
