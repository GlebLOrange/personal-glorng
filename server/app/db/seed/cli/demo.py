"""CLI entrypoint for demo database seeding."""

import argparse
import asyncio

from app.db.seed.demo.run import seed_demo


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
    asyncio.run(
        seed_demo(
            count=args.count,
            reset=args.reset,
            skip_if_populated=args.skip_if_populated,
        )
    )


if __name__ == "__main__":
    main()
