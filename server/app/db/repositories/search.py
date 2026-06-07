from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.search import SearchDocument, SearchVisibility
from app.db.repositories.base import MongoRepository, _parse_doc


class SearchRepository(MongoRepository[SearchDocument]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "search_documents", SearchDocument)

    async def get_by_source(
        self,
        *,
        source_type: str,
        source_id: int,
    ) -> SearchDocument | None:
        data = await self._col().find_one(
            {"source_type": source_type, "source_id": source_id},
        )
        if data is None:
            return None
        return _parse_doc(SearchDocument, data)

    async def upsert(self, document: SearchDocument) -> SearchDocument:
        existing = await self.get_by_source(
            source_type=document.source_type,
            source_id=document.source_id,
        )
        if existing is None:
            document.id = await self.next_id()
            return await self.insert(document)
        document.id = existing.id
        document.created_at = existing.created_at
        return await self.replace(document)

    async def delete_by_source(self, *, source_type: str, source_id: int) -> None:
        await self._col().delete_one(
            {"source_type": source_type, "source_id": source_id},
        )

    async def delete_stale_by_source(
        self,
        source_type: str,
        keep_source_ids: set[int],
    ) -> None:
        query: dict[str, Any] = {"source_type": source_type}
        if keep_source_ids:
            query["source_id"] = {"$nin": list(keep_source_ids)}
        await self._col().delete_many(query)

    async def search_text(
        self,
        query: str,
        *,
        limit: int = 6,
        visibility: str | None = None,
    ) -> list[SearchDocument]:
        mongo_query: dict[str, Any] = {"$text": {"$search": query}}
        if visibility:
            mongo_query["visibility"] = visibility
        cursor = (
            self._col()
            .find(mongo_query, {"score": {"$meta": "textScore"}})
            .sort([("score", {"$meta": "textScore"})])
            .limit(limit)
        )
        return [_parse_doc(SearchDocument, row) async for row in cursor]
