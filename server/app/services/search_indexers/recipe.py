import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.recipe import Recipe
from app.db.models.search_document import SearchVisibility
from app.services.search_index import SearchDocumentInput, SearchIndexService

RECIPE_SOURCE_TYPE = "recipe"


def _loads_list(raw: str) -> list[str]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _recipe_document(recipe: Recipe) -> SearchDocumentInput:
    ingredients = ", ".join(_loads_list(recipe.ingredients))
    steps = " ".join(_loads_list(recipe.steps))
    tags = ", ".join(_loads_list(recipe.tags))
    body_parts = [ingredients, steps]
    if recipe.notes:
        body_parts.append(recipe.notes)
    if tags:
        body_parts.append(f"Tags: {tags}")

    return SearchDocumentInput(
        source_type=RECIPE_SOURCE_TYPE,
        source_id=recipe.id,
        title=recipe.title,
        body="\n".join(body_parts),
        url="/recipes",
        visibility=SearchVisibility.PUBLIC,
    )


async def index_recipe(db: AsyncSession, recipe: Recipe) -> None:
    await SearchIndexService(db).upsert(_recipe_document(recipe))


async def remove_recipe(db: AsyncSession, recipe_id: int) -> None:
    await SearchIndexService(db).delete_by_source(RECIPE_SOURCE_TYPE, recipe_id)
