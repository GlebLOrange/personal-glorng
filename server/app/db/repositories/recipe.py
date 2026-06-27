import json
import re
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.recipe import Recipe
from app.db.repositories.base import MongoRepository, _parse_doc

RECIPE_SORTS: dict[str, list[tuple[str, int]]] = {
    "updated_desc": [("updated_at", -1)],
    "title_asc": [("title", 1)],
    "title_desc": [("title", -1)],
}


def _tag_pattern(tag: str) -> str:
    """Match a complete tag inside the legacy JSON-string tags field."""
    return re.escape(json.dumps(tag))


class RecipeRepository(MongoRepository[Recipe]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "recipes", Recipe)

    @staticmethod
    def _recipe_query(
        *,
        recipe_ids: list[int] | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if recipe_ids is not None:
            query["id"] = {"$in": recipe_ids}
        if tags:
            query["$or"] = [
                {"tags": {"$regex": _tag_pattern(tag)}} for tag in tags if tag
            ]
        return query

    async def count_recipes(
        self,
        *,
        recipe_ids: list[int] | None = None,
        tags: list[str] | None = None,
    ) -> int:
        if recipe_ids == []:
            return 0
        return await self._col().count_documents(
            self._recipe_query(recipe_ids=recipe_ids, tags=tags),
        )

    async def list_recipes(
        self,
        *,
        recipe_ids: list[int] | None = None,
        tags: list[str] | None = None,
        offset: int = 0,
        limit: int = 24,
        sort: str = "updated_desc",
    ) -> list[Recipe]:
        if recipe_ids == []:
            return []
        query = self._recipe_query(recipe_ids=recipe_ids, tags=tags)
        if sort in {"prep_asc", "total_time_asc"}:
            sort_field = "_prep_time" if sort == "prep_asc" else "_total_time"
            cursor = self._col().aggregate(
                [
                    {"$match": query},
                    {
                        "$addFields": {
                            "_total_time": {
                                "$add": [
                                    {"$ifNull": ["$prep_time", 0]},
                                    {"$ifNull": ["$cook_time", 0]},
                                ],
                            },
                            "_prep_time": {"$ifNull": ["$prep_time", 1000000000]},
                        },
                    },
                    {"$sort": {sort_field: 1, "updated_at": -1}},
                    {"$skip": offset},
                    {"$limit": limit},
                ],
            )
            return [_parse_doc(Recipe, row) async for row in cursor]

        sort_spec = RECIPE_SORTS.get(sort, RECIPE_SORTS["updated_desc"])
        cursor = self._col().find(query).sort(sort_spec).skip(offset).limit(limit)
        return [_parse_doc(Recipe, row) async for row in cursor]
