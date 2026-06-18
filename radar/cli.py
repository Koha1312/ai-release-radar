"""AI Release Radar pipeline CLI.

  uv run python -m radar.cli seed     # load curated releases into the DB
  uv run python -m radar.cli ingest   # fetch feeds -> LLM extract -> DB (needs Ollama + network)
  uv run python -m radar.cli build    # export DB -> site/releases.json
  uv run python -m radar.cli refresh  # ingest + build (the daily job)
"""
from __future__ import annotations

import argparse

from . import build_site, seed as seed_mod, store


def cmd_seed(_args) -> None:
    conn = store.connect()
    n = store.upsert_many(conn, seed_mod.all_seed())
    print(f"Seeded {n} curated releases.")


def cmd_ingest(_args) -> None:
    from . import extract, fetch  # imported lazily (feedparser/Ollama only needed here)

    print("Fetching source feeds...")
    items = fetch.fetch_raw()
    print(f"Got {len(items)} raw items. Structuring with local LLM...")
    releases = extract.extract_many(items)
    conn = store.connect()
    n = store.upsert_many(conn, releases)
    print(f"Ingested {n} structured releases.")


def cmd_build(_args) -> None:
    n = build_site.build()
    print(f"Wrote site/releases.json with {n} releases.")


def cmd_refresh(args) -> None:
    cmd_ingest(args)
    cmd_build(args)


def main() -> None:
    parser = argparse.ArgumentParser(prog="radar")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("seed", help="load curated releases")
    sub.add_parser("ingest", help="fetch + LLM-structure new releases")
    sub.add_parser("build", help="export DB to site/releases.json")
    sub.add_parser("refresh", help="ingest + build (daily job)")

    args = parser.parse_args()
    {"seed": cmd_seed, "ingest": cmd_ingest, "build": cmd_build, "refresh": cmd_refresh}[args.command](args)


if __name__ == "__main__":
    main()
