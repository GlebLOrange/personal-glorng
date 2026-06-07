from app.core.json_lists import parse_json_string_list
from app.db.documents.recipe import Recipe
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.search_index import (
    SearchDocumentInput,
    remove_by_source,
    upsert_document,
)
from app.services.search_source_types import SearchSourceType

RECIPE_SOURCE_TYPE = SearchSourceType.RECIPE


def _recipe_document(recipe: Recipe) -> SearchDocumentInput:
    ingredients = ", ".join(parse_json_string_list(recipe.ingredients))
    steps = " ".join(parse_json_string_list(recipe.steps))
    tags = ", ".join(parse_json_string_list(recipe.tags))
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


async def index_recipe(registry: DatabaseRegistry, recipe: Recipe) -> None:
    await upsert_document(registry, _recipe_document(recipe))


async def remove_recipe(registry: DatabaseRegistry, recipe_id: int) -> None:
    await remove_by_source(registry, RECIPE_SOURCE_TYPE, recipe_id)
