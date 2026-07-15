import json
from math import ceil
from typing import Any

from app.core.json_lists import parse_json_string_list
from app.core.logging import logger
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.recipe import Recipe
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.schemas.recipe import (
    RecipeCreate,
    RecipeListResponse,
    RecipeResponse,
    RecipeSort,
    RecipeUpdate,
)
from app.services.audit import AuditService
from app.services.search_index import SearchIndexService
from app.services.search_indexers.recipe import (
    RECIPE_SOURCE_TYPE,
    index_recipe,
    remove_recipe,
)


def _loads_json_list(field: str, raw: str) -> list[str]:
    return parse_json_string_list(raw, strict=True, field=field)


def _dumps_json_list(value: list[str]) -> str:
    return json.dumps(value)


def _recipe_payload_from_create(data: RecipeCreate) -> dict[str, Any]:
    return {
        "title": data.title,
        "ingredients": _dumps_json_list(data.ingredients),
        "steps": _dumps_json_list(data.steps),
        "notes": data.notes,
        "tags": _dumps_json_list(data.tags),
        "image_url": str(data.image_url) if data.image_url else None,
        "prep_time": data.prep_time,
        "cook_time": data.cook_time,
        "servings": data.servings,
    }


def _apply_recipe_updates(recipe: Recipe, data: RecipeUpdate) -> Recipe:
    updates = data.model_dump(exclude_unset=True)

    for field in ("ingredients", "steps", "tags"):
        if field in updates and updates[field] is not None:
            updates[field] = _dumps_json_list(updates[field])

    if "image_url" in updates and updates["image_url"] is not None:
        updates["image_url"] = str(updates["image_url"])

    merged = recipe.model_dump()
    merged.update(updates)
    return Recipe.model_validate(merged)


class RecipeService:
    def __init__(self, registry: DatabaseRegistry, audit_svc: AuditService) -> None:
        self.registry = registry
        self._audit = audit_svc

    def _recipes(self):
        if self.registry.recipes is None:
            msg = "Recipes repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.recipes

    @staticmethod
    def _to_response(recipe: Recipe) -> RecipeResponse:
        return RecipeResponse(
            id=recipe.id,
            title=recipe.title,
            ingredients=_loads_json_list("ingredients", recipe.ingredients),
            steps=_loads_json_list("steps", recipe.steps),
            notes=recipe.notes,
            tags=_loads_json_list("tags", recipe.tags),
            image_url=recipe.image_url,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            servings=recipe.servings,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    async def require_recipe(self, recipe_id: int) -> Recipe:
        return await self._recipes().get(recipe_id)

    async def create_recipe(
        self,
        data: RecipeCreate,
        *,
        actor_id: int | None = None,
    ) -> RecipeResponse:
        recipe = Recipe.model_validate(_recipe_payload_from_create(data))
        recipe = await self._recipes().insert(recipe)
        await index_recipe(self.registry, recipe)
        await self._audit.record_domain(
            action="recipe.created",
            resource_type="recipe",
            resource_id=recipe.id,
            actor_id=actor_id,
            metadata={"title": recipe.title},
        )
        return self._to_response(recipe)

    async def update_recipe(
        self,
        recipe_id: int,
        data: RecipeUpdate,
        *,
        actor_id: int | None = None,
    ) -> RecipeResponse:
        recipe = await self.require_recipe(recipe_id)
        updated = _apply_recipe_updates(recipe, data)
        recipe = await self._recipes().replace(updated)
        await index_recipe(self.registry, recipe)
        await self._audit.record_domain(
            action="recipe.updated",
            resource_type="recipe",
            resource_id=recipe.id,
            actor_id=actor_id,
        )
        return self._to_response(recipe)

    async def delete_recipe(
        self,
        recipe_id: int,
        *,
        actor_id: int | None = None,
    ) -> None:
        await self.require_recipe(recipe_id)
        await self._recipes().delete(recipe_id)
        await remove_recipe(self.registry, recipe_id)
        await self._audit.record_domain(
            action="recipe.deleted",
            resource_type="recipe",
            resource_id=recipe_id,
            actor_id=actor_id,
        )

    async def list_recipes(
        self,
        search: str | None = None,
        tags: list[str] | None = None,
        sort: RecipeSort = "updated_desc",
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> RecipeListResponse:
        offset, limit = paginate_params(page, per_page)
        recipe_ids: list[int] | None = None
        if search:
            results = await SearchIndexService(self.registry).search(
                search,
                visibilities=[SearchVisibility.PUBLIC],
                source_types=[RECIPE_SOURCE_TYPE],
                limit=500,
            )
            recipe_ids = [hit.source_id for hit in results]

        total = await self._recipes().count_recipes(recipe_ids=recipe_ids, tags=tags)
        items = await self._recipes().list_recipes(
            recipe_ids=recipe_ids,
            tags=tags,
            offset=offset,
            limit=limit,
            sort=sort,
        )
        pages = ceil(total / limit) if total > 0 else 0

        return RecipeListResponse(
            items=[self._to_response(r) for r in items],
            total=total,
            page=page,
            per_page=limit,
            pages=pages,
        )

    async def get_recipe(self, recipe_id: int) -> RecipeResponse:
        recipe = await self.require_recipe(recipe_id)
        return self._to_response(recipe)

    async def get_all_tags(self) -> list[str]:
        all_recipes = await self._recipes().list(limit=10_000)
        all_tags: set[str] = set()
        for recipe in all_recipes:
            try:
                tags = json.loads(recipe.tags)
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping recipe row with corrupted tags JSON",
                    context={"tags_json": recipe.tags},
                )
                continue
            if not isinstance(tags, list):
                logger.warning(
                    "Skipping recipe row with invalid tags JSON shape",
                    context={"tags_json": recipe.tags},
                )
                continue
            for tag in tags:
                if isinstance(tag, str):
                    all_tags.add(tag)
        return sorted(all_tags)
