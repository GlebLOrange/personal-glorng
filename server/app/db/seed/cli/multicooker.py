"""Seed multicooker-friendly recipes fetched from TheMealDB."""

import json

from app.core.logging import logger
from app.db.documents.recipe import Recipe
from app.db.registry import DatabaseRegistry
from app.services.themealdb import ThemealDBClient

DEFAULT_MULTICOOKER_COUNT = 100


async def seed_multicooker_recipes(
    registry: DatabaseRegistry,
    count: int = DEFAULT_MULTICOOKER_COUNT,
) -> int:
    """Fetch recipes from TheMealDB and insert new ones into MongoDB.

    Caller owns registry startup/shutdown. Returns inserted count.
    """
    if registry.recipes is None:
        msg = "Recipes repository is not initialized"
        raise RuntimeError(msg)

    client = ThemealDBClient()
    candidates = await client.fetch_multicooker_candidates(limit=count)

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
    return inserted
