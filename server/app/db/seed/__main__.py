"""CLI entrypoint for ``python -m app.db.seed`` / ``make seed-db``."""

from __future__ import annotations

import argparse
import asyncio

from pymongo.errors import DuplicateKeyError

from app.db.seed import seed
from app.db.seed.demo.run import (
    SEED_DEMO_RECIPES,
    SEED_EXPENSES,
    SEED_FEEDBACK,
    SEED_MULTICOOKER_RECIPES,
    SEED_NEWS,
    SEED_SHORT_URLS,
    SEED_TASKS,
    SEED_TOOL_NAMES,
    SeedPlan,
)


def _duplicate_key_field(exc: DuplicateKeyError) -> str | None:
    """Return the Mongo duplicate key field when included by the driver."""
    key_pattern = (exc.details or {}).get("keyPattern") or {}
    if len(key_pattern) == 1:
        return next(iter(key_pattern))
    if "link_1" in str(exc) or "link" in str(exc):
        return "link"
    return None


def _parse_only(value: str) -> frozenset[str]:
    """Parse a comma-separated tool list for ``--only``."""
    tools = {part.strip() for part in value.split(",") if part.strip()}
    unknown = tools - SEED_TOOL_NAMES
    if unknown:
        allowed = ", ".join(sorted(SEED_TOOL_NAMES))
        bad = ", ".join(sorted(unknown))
        msg = f"Unknown tool(s): {bad}. Allowed: {allowed}"
        raise argparse.ArgumentTypeError(msg)
    if not tools:
        msg = "Provide at least one tool name"
        raise argparse.ArgumentTypeError(msg)
    return frozenset(tools)


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
            "Wipe tool tables before seeding (default: true). Use --no-reset to append."
        ),
    )
    parser.add_argument(
        "--skip-if-populated",
        action="store_true",
        help=(
            "Skip tool seeding when recipes already exist and recipes are in the plan "
            "(still ensures users)."
        ),
    )
    parser.add_argument(
        "--only",
        type=_parse_only,
        default=None,
        metavar="TOOLS",
        help=(
            "Comma-separated tools to seed: "
            "recipes,multicooker,expenses,tasks,news,urls,feedback. "
            "Users are always ensured."
        ),
    )
    parser.add_argument(
        "--no-multicooker",
        action="store_true",
        help="Skip live TheMealDB multicooker recipe fetch.",
    )
    parser.add_argument(
        "--recipes",
        type=int,
        default=SEED_DEMO_RECIPES,
        help=f"Demo recipe count (default: {SEED_DEMO_RECIPES}). Use 0 to skip.",
    )
    parser.add_argument(
        "--multicooker",
        type=int,
        default=SEED_MULTICOOKER_RECIPES,
        help=(
            f"Multicooker recipe count (default: {SEED_MULTICOOKER_RECIPES}). "
            "Use 0 to skip."
        ),
    )
    parser.add_argument(
        "--expenses",
        type=int,
        default=SEED_EXPENSES,
        help=f"Expense count (default: {SEED_EXPENSES}). Use 0 to skip.",
    )
    parser.add_argument(
        "--tasks",
        type=int,
        default=SEED_TASKS,
        help=f"Task count (default: {SEED_TASKS}). Use 0 to skip.",
    )
    parser.add_argument(
        "--news",
        type=int,
        default=SEED_NEWS,
        help=f"News article count (default: {SEED_NEWS}). Use 0 to skip.",
    )
    parser.add_argument(
        "--urls",
        type=int,
        default=SEED_SHORT_URLS,
        help=f"Short URL count (default: {SEED_SHORT_URLS}). Use 0 to skip.",
    )
    parser.add_argument(
        "--feedback",
        type=int,
        default=SEED_FEEDBACK,
        help=f"Feedback count (default: {SEED_FEEDBACK}). Use 0 to skip.",
    )
    return parser.parse_args()


def plan_from_args(args: argparse.Namespace) -> SeedPlan:
    """Build a ``SeedPlan`` from parsed CLI arguments."""
    return SeedPlan(
        recipes=args.recipes,
        multicooker=args.multicooker,
        expenses=args.expenses,
        tasks=args.tasks,
        news=args.news,
        urls=args.urls,
        feedback=args.feedback,
        enabled=args.only,
        multicooker_fetch=not args.no_multicooker,
    )


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    try:
        asyncio.run(
            seed(
                reset=args.reset,
                skip_if_populated=args.skip_if_populated,
                plan=plan_from_args(args),
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
