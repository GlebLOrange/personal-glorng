"""MongoDB repository for promoted embed items."""

from __future__ import annotations

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.embed_item import EmbedItem
from app.db.repositories.base import MongoRepository


class EmbedItemRepository(MongoRepository[EmbedItem]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "embed_items", EmbedItem)

    async def upsert_by_embed_id(self, item: EmbedItem) -> EmbedItem:
        """Insert or replace an embed item keyed by ``embed_id``."""
        existing = await self._col().find_one({"embed_id": item.embed_id})
        if existing is None:
            return await self.insert(item)
        item.id = int(existing["id"])
        item.created_at = existing.get("created_at", item.created_at)
        return await self.replace(item)
