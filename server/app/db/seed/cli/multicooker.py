"""Seed multicooker-friendly recipes fetched from TheMealDB."""

import argparse
import asyncio
import json

from app.core.logging import logger
from app.db.documents.recipe import Recipe
from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.services.themealdb import ThemealDBClient
from app.settings import get_settings


async def seed_multicooker_recipes(count: int = 25) -> None:
    """Fetch recipes from TheMealDB and insert new ones into MongoDB."""
    client = ThemealDBClient()
    candidates = await client.fetch_multicooker_candidates(limit=count)

    settings = get_settings()
    registry = DatabaseRegistry()
    init_svc = DatabaseInitService(registry, settings)
    try:
        await init_svc.startup()
        if registry.recipes is None:
            msg = "Recipes repository is not initialized"
            raise RuntimeError(msg)

        existing = await registry.recipes.list(limit=10_000)
        existing_titles = {recipe.title for recipe in existing}
        inserted = 0
        skipped = 0

        for data in candidates:
            if data["title"] in existing_titles:
                skipped += 1
                continue

            await registry.recipes.insert(
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
                ),
            )
            inserted += 1

        logger.info(
            "Multicooker recipe seed complete",
            context={"inserted": inserted, "skipped": skipped},
        )
    finally:
        await init_svc.shutdown()


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Seed multicooker recipes from TheMealDB")
    parser.add_argument("--count", type=int, default=25, help="Max recipes to fetch")
    args = parser.parse_args()
    asyncio.run(seed_multicooker_recipes(count=args.count))


if __name__ == "__main__":
    main()
