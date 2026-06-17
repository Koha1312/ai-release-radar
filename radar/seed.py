"""Curated seed data: real AI releases (June 2026), source-cited.

This gives the site real content out of the box. The live pipeline
(fetch -> extract) appends to this over time.
"""
from __future__ import annotations

from .schema import Release, ReleaseType

SEED: list[Release] = [
    Release(
        company="Anthropic", product="Claude Fable 5",
        title="Anthropic releases Claude Fable 5 (then suspends it)",
        summary="A Mythos-class model with a 1M-token context, 128k max output, and always-on adaptive thinking — made generally available June 9, then suspended June 12 under a US export-control directive.",
        date="2026-06-09", type=ReleaseType.MODEL,
        url="https://www.infoq.com/news/2026/06/claude-5-release/",
        tags=["1M context", "long-horizon", "suspended"],
    ),
    Release(
        company="Anthropic", product="Claude Mythos 5",
        title="Claude Mythos 5 launches for trusted access",
        summary="Frontier Mythos-class model on the Claude Developer Platform alongside Fable 5; also suspended June 12 under the same export directive.",
        date="2026-06-09", type=ReleaseType.MODEL,
        url="https://www.infoq.com/news/2026/06/claude-5-release/",
        tags=["frontier", "suspended"],
    ),
    Release(
        company="Anthropic", product="Claude Opus 4.8",
        title="Claude Opus 4.8 is the new top-tier model",
        summary="Anthropic's latest flagship — an upgrade for coding, agentic tasks, and professional work.",
        date="2026-06-10", type=ReleaseType.MODEL,
        url="https://releasebot.io/updates/anthropic/claude",
        tags=["coding", "agentic", "flagship"],
    ),
    Release(
        company="Anthropic", product="Legal MCP connectors",
        title="20+ legal MCP connectors and 12 practice-area plugins",
        summary="Expands how law firms and in-house teams use Claude across research, contracts, discovery, matter management, and legal aid.",
        date="2026-06-11", type=ReleaseType.FEATURE,
        url="https://releasebot.io/updates/anthropic",
        tags=["MCP", "legal", "connectors"],
    ),
    Release(
        company="OpenAI", product="GPT-5.5",
        title="OpenAI introduces GPT-5.5",
        summary="Described as their smartest model yet — faster and built for complex coding, research, and data analysis across tools.",
        date="2026-06-05", type=ReleaseType.MODEL,
        url="https://openai.com/index/gpt-5-5-instant/",
        tags=["flagship", "reasoning"],
    ),
    Release(
        company="OpenAI", product="GPT-5.3-Codex",
        title="GPT-5.3-Codex: most capable agentic coding model",
        summary="Combines the Codex + GPT-5 training stacks into one unified model for code generation, reasoning, and general intelligence.",
        date="2026-06-04", type=ReleaseType.MODEL,
        url="https://help.openai.com/en/articles/9624314-model-release-notes",
        tags=["coding", "agentic"],
    ),
    Release(
        company="OpenAI", product="GPT-5.2",
        title="GPT-5.2 retired from ChatGPT",
        summary="GPT-5.2 Instant/Thinking/Pro removed June 12; existing chats auto-continue on GPT-5.5.",
        date="2026-06-12", type=ReleaseType.DEPRECATION,
        url="https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
        tags=["retirement"],
    ),
    Release(
        company="OpenAI", product="GPT-4.5",
        title="GPT-4.5 sunsetting June 27",
        summary="GPT-4.5 will be retired from ChatGPT on June 27, 2026 after a 30-day sunset.",
        date="2026-06-27", type=ReleaseType.DEPRECATION,
        url="https://help.openai.com/en/articles/6825453-chatgpt-release-notes",
        tags=["retirement", "scheduled"],
    ),
    Release(
        company="Google", product="Gemini 3.5 Flash",
        title="Gemini 3.5 Flash goes generally available",
        summary="Released May 19; now GA across Global, US, and EU regions with Gemini Enterprise.",
        date="2026-05-19", type=ReleaseType.MODEL,
        url="https://ai.google.dev/gemini-api/docs/changelog",
        tags=["fast", "GA", "enterprise"],
    ),
    Release(
        company="Google", product="Gemini Omni",
        title="Gemini Omni — native video creation",
        summary="A new AI video model that combines text, images, audio, and video as inputs, unveiled at I/O 2026.",
        date="2026-05-19", type=ReleaseType.MODEL,
        url="https://techcrunch.com/2026/05/19/google-updates-its-gemini-app-to-take-on-chatgpt-and-claude-at-io-2026/",
        tags=["video", "multimodal"],
    ),
    Release(
        company="Google", product="Gemini Spark + Daily Brief",
        title="Gemini app gains a personal agent and Daily Brief",
        summary="The Gemini app added 'Spark' (a personal AI agent), a 'Daily Brief' feature, and a redesigned interface.",
        date="2026-05-19", type=ReleaseType.FEATURE,
        url="https://techcrunch.com/2026/05/19/google-updates-its-gemini-app-to-take-on-chatgpt-and-claude-at-io-2026/",
        tags=["agent", "app"],
    ),
    Release(
        company="Google", product="Gemini 3 Deep Think",
        title="Gemini 3 Deep Think for AI Ultra subscribers",
        summary="Google's top reasoning mode for math, science, logic, and hard multi-step problems.",
        date="2026-05-20", type=ReleaseType.FEATURE,
        url="https://blog.mean.ceo/google-gemini-news-june-2026/",
        tags=["reasoning"],
    ),
    Release(
        company="Microsoft", product="Azure AI Foundry",
        title="Azure AI Foundry headlines Build 2026",
        summary="A central model-routing layer that picks the right model per task so teams aren't locked in — a core theme of Build 2026.",
        date="2026-06-02", type=ReleaseType.PLATFORM,
        url="https://www.tomsguide.com/news/live/microsoft-build-2026",
        tags=["Azure", "routing", "Build 2026"],
    ),
    Release(
        company="Microsoft", product="MAI models (Thinking-1, Code-1)",
        title="Seven new in-house MAI models",
        summary="Includes MAI-Thinking-1 (reasoning) and MAI-Code-1, tuned specifically for GitHub and VS Code.",
        date="2026-06-02", type=ReleaseType.MODEL,
        url="https://www.tomsguide.com/news/live/microsoft-build-2026",
        tags=["MAI", "coding", "Build 2026"],
    ),
    Release(
        company="Microsoft", product="Windows Agent Runtime",
        title="Windows Agent Runtime + Copilot Platform",
        summary="Turns Windows into an AI-agent platform; rolling out in preview, with general availability slated for November 2026.",
        date="2026-06-02", type=ReleaseType.PLATFORM,
        url="https://windowsnews.ai/article/build-2026-microsoft-turns-windows-copilot-and-azure-into-an-ai-agent-platform.421835",
        tags=["Windows", "agents", "preview"],
    ),
    Release(
        company="Microsoft", product="Microsoft Agent 365",
        title="Microsoft Agent 365 reaches general availability",
        summary="An enterprise control plane for managing AI agents; GA since May 1, expanded at Build 2026.",
        date="2026-05-01", type=ReleaseType.PLATFORM,
        url="https://www.tomsguide.com/news/live/microsoft-build-2026",
        tags=["enterprise", "agents", "governance"],
    ),
]
