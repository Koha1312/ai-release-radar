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
    """Daily job: curated baseline + past discoveries + fresh RSS, then rebuild.

    Order matters so nothing is ever lost: seed the 108 curated releases first,
    re-load past auto-discoveries from releases.json, THEN ingest new RSS items.
    Even if ingestion fails entirely, the site still rebuilds from the baseline.
    """
    from . import extract, fetch

    conn = store.connect()
    store.upsert_many(conn, seed_mod.all_seed())
    kept = build_site.load_existing(conn)
    print(f"Baseline ready: curated seed + {kept} existing releases.")

    seen = store.seen_urls(conn)
    raw = fetch.fetch_raw()
    fresh = [it for it in raw if it.get("url") and it["url"] not in seen]
    print(f"Fetched {len(raw)} items; {len(fresh)} new (skipped {len(raw) - len(fresh)} already seen).")

    CAP = 25  # flood guard: a sudden surge signals a feed glitch/attack — process at most this many
    if len(fresh) > CAP:
        print(f"  ! flood guard: {len(fresh)} new items — capping to {CAP} this run (rest come next run)")
        fresh = fresh[:CAP]

    releases = extract.extract_many(fresh)  # only NEW items hit the LLM
    store.upsert_many(conn, releases)

    n = build_site.build()
    print(f"Refreshed: {n} releases total (+{len(releases)} new this run).")


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
