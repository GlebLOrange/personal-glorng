import json
from math import ceil
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

from app.core.exceptions import ApiError, NotFoundError
from app.core.logging import logger
from app.core.utils import paginate_params
from app.db.models.recipe import Recipe
from app.db.recipe_search import RECIPE_SEARCH_CONFIG
from app.schemas.recipe import RecipeCreate, RecipeListResponse, RecipeResponse, RecipeSort, RecipeUpdate
from app.services.audit import AuditService
from app.services.base import CRUDService
from app.services.search_indexers.recipe import index_recipe, remove_recipe


def _recipe_search_vector() -> ColumnElement:
    return func.to_tsvector(
        RECIPE_SEARCH_CONFIG,
        func.concat(
            Recipe.title,
            " ",
            Recipe.ingredients,
            " ",
            Recipe.steps,
            " ",
            func.coalesce(Recipe.notes, ""),
        ),
    )


def _loads_json_list(field: str, raw: str) -> list[str]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ApiError(
            500,
            f"Recipe {field} data is corrupted",
            is_operational=False,
        ) from exc
    if not isinstance(value, list):
        raise ApiError(
            500,
            f"Recipe {field} data is corrupted",
            is_operational=False,
        )
    return value


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


def _apply_recipe_updates(recipe: Recipe, data: RecipeUpdate) -> None:
    updates = data.model_dump(exclude_unset=True)

    for field in ("ingredients", "steps", "tags"):
        if field in updates and updates[field] is not None:
            updates[field] = _dumps_json_list(updates[field])

    if "image_url" in updates and updates["image_url"] is not None:
        updates["image_url"] = str(updates["image_url"])

    for key, value in updates.items():
        setattr(recipe, key, value)


class RecipeService(CRUDService[Recipe]):
    def __init__(self, db: AsyncSession, audit_svc: AuditService) -> None:
        super().__init__(db, Recipe)
        self._audit = audit_svc

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
        result = await self.db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = result.scalar_one_or_none()
        if not recipe:
            raise NotFoundError("Recipe not found")
        return recipe

    async def create_recipe(
        self,
        data: RecipeCreate,
        *,
        actor_id: int | None = None,
    ) -> RecipeResponse:
        recipe = await self.create(_recipe_payload_from_create(data))
        await index_recipe(self.db, recipe)
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
        _apply_recipe_updates(recipe, data)

        await self.db.flush()
        await self.db.refresh(recipe)
        await index_recipe(self.db, recipe)
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
        await self.delete(recipe_id)
        await remove_recipe(self.db, recipe_id)
        await self._audit.record_domain(
            action="recipe.deleted",
            resource_type="recipe",
            resource_id=recipe_id,
            actor_id=actor_id,
        )

    def _recipe_list_filters(
        self,
        search: str | None,
        tag: str | None,
    ) -> list[ColumnElement[bool]]:
        filters: list[ColumnElement[bool]] = []
        if search:
            dialect_name = self.db.get_bind().dialect.name
            if dialect_name == "postgresql":
                ts_query = func.plainto_tsquery(RECIPE_SEARCH_CONFIG, search)
                filters.append(_recipe_search_vector().bool_op("@@")(ts_query))
            else:
                pattern = f"%{search}%"
                filters.append(
                    or_(
                        Recipe.title.ilike(pattern),
                        Recipe.ingredients.ilike(pattern),
                        Recipe.steps.ilike(pattern),
                        Recipe.notes.ilike(pattern),
                    )
                )
        if tag:
            filters.append(Recipe.tags.ilike(f'%"{tag}"%'))
        return filters

    @staticmethod
    def _recipe_sort_clause(sort: RecipeSort) -> ColumnElement:
        total_time = func.coalesce(Recipe.prep_time, 0) + func.coalesce(Recipe.cook_time, 0)
        match sort:
            case "title_asc":
                return Recipe.title.asc()
            case "title_desc":
                return Recipe.title.desc()
            case "prep_asc":
                return Recipe.prep_time.asc().nulls_last()
            case "total_time_asc":
                return total_time.asc().nulls_last()
            case _:
                return Recipe.updated_at.desc()

    async def list_recipes(
        self,
        search: str | None = None,
        tag: str | None = None,
        sort: RecipeSort = "updated_desc",
        page: int = 1,
        per_page: int = 24,
    ) -> RecipeListResponse:
        offset, limit = paginate_params(page, per_page)
        filters = self._recipe_list_filters(search=search, tag=tag)

        count_query = select(func.count()).select_from(Recipe)
        for clause in filters:
            count_query = count_query.where(clause)
        total = int((await self.db.execute(count_query)).scalar_one())

        query = select(Recipe)
        for clause in filters:
            query = query.where(clause)
        query = query.order_by(self._recipe_sort_clause(sort)).offset(offset).limit(limit)

        result = await self.db.execute(query)
        items = [self._to_response(r) for r in result.scalars().all()]
        pages = ceil(total / limit) if total > 0 else 0

        return RecipeListResponse(
            items=items,
            total=total,
            page=page,
            per_page=limit,
            pages=pages,
        )

    async def get_recipe(self, recipe_id: int) -> RecipeResponse:
        recipe = await self.require_recipe(recipe_id)
        return self._to_response(recipe)

    async def get_all_tags(self) -> list[str]:
        result = await self.db.execute(select(Recipe.tags))
        all_tags: set[str] = set()
        for (tags_json,) in result:
            try:
                tags = json.loads(tags_json)
            except json.JSONDecodeError:
                logger.warning(
                    "Skipping recipe row with corrupted tags JSON",
                    context={"tags_json": tags_json},
                )
                continue
            if not isinstance(tags, list):
                logger.warning(
                    "Skipping recipe row with invalid tags JSON shape",
                    context={"tags_json": tags_json},
                )
                continue
            for tag in tags:
                if isinstance(tag, str):
                    all_tags.add(tag)
        return sorted(all_tags)
