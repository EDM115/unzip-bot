from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from unzipbot.config.defaults import Defaults  # noqa: E402
from unzipbot.db.migration import migrate_atlas_if_needed  # noqa: E402


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Migrate unzip-bot MongoDB Atlas data from legacy collections "
            "to v7 SQL-shaped collections."
        )
    )
    parser.add_argument("--mongo-url", default=os.environ.get("MONGODB_URL"))
    parser.add_argument(
        "--target-db",
        default=os.environ.get("MONGODB_DBNAME") or Defaults.MONGODB_DBNAME,
        help="Database that will receive the new schema collections.",
    )
    parser.add_argument(
        "--source-db", default=None, help="Optional legacy database to inspect first."
    )
    parser.add_argument("--base-language", default=os.environ.get("BASE_LANGUAGE") or "en")
    return parser


async def _main() -> int:
    args = _parser().parse_args()
    if not args.mongo_url:
        print("MONGODB_URL is required, either as env var or --mongo-url.", file=sys.stderr)
        return 2

    stats = await migrate_atlas_if_needed(
        connection_str=args.mongo_url,
        target_db_name=args.target_db,
        source_db_name=args.source_db,
        base_language=args.base_language,
    )
    print("Atlas schema migration completed successfully.")
    print(stats.summary)
    if stats.tables:
        for table_name, count in sorted(stats.tables.items()):
            print(f"- {table_name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
