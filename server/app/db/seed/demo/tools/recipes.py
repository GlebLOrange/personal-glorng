"""Demo recipe seeding."""

from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_random_recipes, build_recipe_tag_pool


async def seed_demo_recipes(registry: DatabaseRegistry, count: int) -> int:
    """Insert procedurally generated recipes."""
    if registry.recipes is None:
        msg = "Recipes repository is not initialized"
        raise RuntimeError(msg)

    tag_pool = build_recipe_tag_pool(count)
    recipes = build_random_recipes(count, tag_pool)
    for recipe in recipes:
        await registry.recipes.insert(recipe)
    return len(recipes)
