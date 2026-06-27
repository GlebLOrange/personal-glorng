"""CLI entrypoint for demo database seeding."""

import argparse
import asyncio

from pymongo.errors import DuplicateKeyError

from app.db.seed.demo.run import seed_demo


def _duplicate_key_field(exc: DuplicateKeyError) -> str | None:
    """Return the Mongo duplicate key field when included by the driver."""
    key_pattern = (exc.details or {}).get("keyPattern") or {}
    if len(key_pattern) == 1:
        return next(iter(key_pattern))
    if "link_1" in str(exc) or "link" in str(exc):
        return "link"
    return None


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=("Fill the database with random demo data for each platform tool."),
    )
    parser.add_argument(
        "--count",
        type=int,
        default=50,
        help="Number of records to create per tool (default: 50).",
    )
    parser.add_argument(
        "--reset",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Wipe tool tables before seeding (default: true). Use --no-reset to append."
        ),
    )
    parser.add_argument(
        "--skip-if-populated",
        action="store_true",
        help="Skip tool seeding when recipes already exist (still ensures demo users).",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be at least 1")
    try:
        asyncio.run(
            seed_demo(
                count=args.count,
                reset=args.reset,
                skip_if_populated=args.skip_if_populated,
            )
        )
    except DuplicateKeyError as exc:
        if _duplicate_key_field(exc) != "link":
            raise
        raise SystemExit(
            "Obsolete unique news_articles.link index found. "
            "Run migrations/schema init, then retry make seed-demo."
        ) from exc


if __name__ == "__main__":
    main()
