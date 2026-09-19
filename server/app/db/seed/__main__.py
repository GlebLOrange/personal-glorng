"""CLI entrypoint for ``python -m app.db.seed`` / ``make seed-db``."""

import argparse
import asyncio

from pymongo.errors import DuplicateKeyError

from app.db.seed import seed


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
        description="Seed the database with fixed-volume mock test data.",
    )
    parser.add_argument(
        "--reset",
        action=argparse.BooleanOptionalAction,
        default=True,
        help=(
            "Wipe tool tables before seeding (default: true). "
            "Use --no-reset to append."
        ),
    )
    parser.add_argument(
        "--skip-if-populated",
        action="store_true",
        help="Skip tool seeding when recipes already exist (still ensures users).",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    try:
        asyncio.run(
            seed(
                reset=args.reset,
                skip_if_populated=args.skip_if_populated,
            )
        )
    except DuplicateKeyError as exc:
        if _duplicate_key_field(exc) != "link":
            raise
        raise SystemExit(
            "Obsolete unique news_articles.link index found. "
            "Run migrations/schema init, then retry make seed-db."
        ) from exc


if __name__ == "__main__":
    main()
