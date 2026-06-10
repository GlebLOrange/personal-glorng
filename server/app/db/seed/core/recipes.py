"""Sample recipe seeding for core dev seed."""

import json
import random
from pathlib import Path

from app.core.logging import logger
from app.db.documents.recipe import Recipe
from app.db.registry import DatabaseRegistry
from app.db.seed.core.admin import require_repos

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "sample_recipes.json"


def load_sample_recipes() -> list[dict]:
    """Load bundled sample recipe payloads."""
    return json.loads(_DATA_PATH.read_text(encoding="utf-8"))


async def seed_recipes(registry: DatabaseRegistry) -> None:
    """Insert sample recipes if the collection is empty."""
    require_repos(registry)
    count = await registry.recipes.count()
    if count:
        logger.info("Recipes already seeded", context={"count": count})
        return

    recipes = list(load_sample_recipes())
    random.shuffle(recipes)

    for data in recipes:
        recipe = Recipe(
            title=data["title"],
            ingredients=json.dumps(data["ingredients"]),
            steps=json.dumps(data["steps"]),
            tags=json.dumps(data["tags"]),
            prep_time=data.get("prep_time"),
            cook_time=data.get("cook_time"),
            servings=data.get("servings"),
        )
        await registry.recipes.insert(recipe)

    logger.info("Seeded sample recipes", context={"count": len(recipes)})
