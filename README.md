# 🛰️ AI Release Radar

A structured, source-cited tracker of **AI releases worth knowing** — from the
big labs (Anthropic, OpenAI, Google, Microsoft, Meta…) to the AI tools & apps we
actually use (Perplexity, Cursor…). Not another news blog — a *curated,
deduplicated database* of real releases you can filter and trust.

## Why it's built as a pipeline (not just a page)

```
sources (RSS) → LLM extract & structure → SQLite (dedup) → releases.json → static site
```

- **Ingestion** pulls from source feeds (best-effort; dead feeds are skipped).
- **A local LLM** (Ollama) decides if an item is a real release and normalizes it
  into one schema — noise is dropped, not tracked.
- **SQLite** dedups so the same release from multiple sources collapses to one row.
- **The site** is fully static (reads `releases.json`) → deploys anywhere, no backend.

## Run it

```bash
uv sync
uv run python -m radar.cli seed      # load curated real releases
uv run python -m radar.cli build     # generate site/releases.json
# serve the static site:
python -m http.server 8200 --directory site   # → http://localhost:8200
```

Keep it fresh (needs Ollama running + network):

```bash
uv run python -m radar.cli refresh   # ingest new feed items + rebuild
```

## 🤖 Use it from an AI assistant (MCP)

A built-in MCP server lets Claude (Code or Desktop) query the radar live —
ask *"what open-source models dropped this week?"* and it calls the radar.

Add this to your MCP config (e.g. Claude Desktop `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ai-release-radar": {
      "command": "uv",
      "args": ["run", "--directory", "C:/Users/koha/ai-release-radar", "python", "-m", "radar.mcp_server"]
    }
  }
}
```

Tools exposed: `search_releases` (by company / type / open-source / recency / text),
`list_companies`, and `radar_stats`.

## Deploy

The `site/` folder is a static site — point Vercel / Netlify / GitHub Pages at it.
Re-run `refresh` (locally or in CI) to update `releases.json`, then redeploy.

## Roadmap (this is a learning project too)

- [ ] GitHub Action to run `refresh` daily and commit `releases.json`
- [ ] Cross-source dedup by entity (same release, different headlines)
- [ ] An LLM-written "daily digest" summary
- [ ] Add Meta, Mistral, xAI, DeepSeek sources

---

*Built by **Khoa Nguyen**, paired with Claude 💙*
