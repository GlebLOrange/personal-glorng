"""Seed multicooker-friendly recipes fetched from TheMealDB."""

import argparse
import asyncio
import json

from sqlalchemy import select

from app.core.logging import logger
from app.db.models.recipe import Recipe
from app.db.session import get_session_factory
from app.services.themealdb import ThemealDBClient


async def seed_multicooker_recipes(count: int = 25) -> None:
    """Fetch recipes from TheMealDB and insert new ones into the database."""
    client = ThemealDBClient()
    candidates = await client.fetch_multicooker_candidates(limit=count)

    async with get_session_factory()() as db:
        existing_titles = set(await db.scalars(select(Recipe.title)))
        inserted = 0
        skipped = 0

        for data in candidates:
            if data["title"] in existing_titles:
                skipped += 1
                continue

            db.add(
                Recipe(
                    title=data["title"],
                    ingredients=json.dumps(data["ingredients"]),
                    steps=json.dumps(data["steps"]),
                    notes=data.get("notes"),
                    tags=json.dumps(data["tags"]),
                    image_url=data.get("image_url"),
                    prep_time=data.get("prep_time"),
                    cook_time=data.get("cook_time"),
                    servings=data.get("servings"),
                )
            )
            existing_titles.add(data["title"])
            inserted += 1

        await db.commit()

    logger.info(
        "Seeded multicooker recipes",
        context={
            "inserted": inserted,
            "skipped": skipped,
            "requested": count,
            "fetched": len(candidates),
        },
    )


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Fetch easy multicooker recipes from TheMealDB "
            "and insert them into the database."
        ),
    )
    parser.add_argument(
        "--count",
        type=int,
        default=25,
        help="Number of recipes to fetch and attempt to insert (default: 25).",
    )
    return parser.parse_args()


def main() -> None:
    """CLI entrypoint."""
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be at least 1")
    asyncio.run(seed_multicooker_recipes(count=args.count))


if __name__ == "__main__":
    main()
