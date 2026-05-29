import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_event import AuditActorType, AuditCategory, AuditSource
from app.db.models.recipe import Recipe
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.services.audit import AuditRecord, AuditService
from app.services.base import CRUDService


class RecipeService(CRUDService[Recipe]):
    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, Recipe)

    @staticmethod
    def _to_response(recipe: Recipe) -> RecipeResponse:
        return RecipeResponse(
            id=recipe.id,
            title=recipe.title,
            ingredients=json.loads(recipe.ingredients),
            steps=json.loads(recipe.steps),
            notes=recipe.notes,
            tags=json.loads(recipe.tags),
            image_url=recipe.image_url,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            servings=recipe.servings,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
        )

    async def create_recipe(self, data: RecipeCreate) -> RecipeResponse:
        recipe = await self.create({
            "title": data.title,
            "ingredients": json.dumps(data.ingredients),
            "steps": json.dumps(data.steps),
            "notes": data.notes,
            "tags": json.dumps(data.tags),
            "image_url": data.image_url,
            "prep_time": data.prep_time,
            "cook_time": data.cook_time,
            "servings": data.servings,
        })
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="recipe.created",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="recipe",
                resource_id=recipe.id,
                metadata={"title": recipe.title},
            ),
        )
        return self._to_response(recipe)

    async def update_recipe(self, recipe_id: int, data: RecipeUpdate) -> RecipeResponse:
        recipe = await self.get(recipe_id)
        updates = data.model_dump(exclude_unset=True)

        for field in ("ingredients", "steps", "tags"):
            if field in updates and updates[field] is not None:
                updates[field] = json.dumps(updates[field])

        for key, value in updates.items():
            setattr(recipe, key, value)

        await self.db.flush()
        await self.db.refresh(recipe)
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="recipe.updated",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="recipe",
                resource_id=recipe.id,
            ),
        )
        return self._to_response(recipe)

    async def delete_recipe(self, recipe_id: int) -> None:
        await self.delete(recipe_id)
        await AuditService(self.db).record(
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action="recipe.deleted",
                actor_type=AuditActorType.USER,
                source=AuditSource.WEB_ADMIN,
                resource_type="recipe",
                resource_id=recipe_id,
            ),
        )

    async def list_recipes(
        self,
        search: str | None = None,
        tag: str | None = None,
    ) -> list[RecipeResponse]:
        query = select(Recipe).order_by(Recipe.created_at.desc())

        if search:
            query = query.where(Recipe.title.ilike(f"%{search}%"))
        if tag:
            query = query.where(Recipe.tags.ilike(f'%"{tag}"%'))

        result = await self.db.execute(query)
        return [self._to_response(r) for r in result.scalars().all()]

    async def get_recipe(self, recipe_id: int) -> RecipeResponse:
        recipe = await self.get(recipe_id)
        return self._to_response(recipe)

    async def get_all_tags(self) -> list[str]:
        result = await self.db.execute(select(Recipe.tags))
        all_tags: set[str] = set()
        for (tags_json,) in result:
            for t in json.loads(tags_json):
                all_tags.add(t)
        return sorted(all_tags)
