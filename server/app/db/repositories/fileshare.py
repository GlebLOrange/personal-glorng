from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.fileshare import SharedFile
from app.db.repositories.base import MongoRepository, _parse_doc


class FileShareRepository(MongoRepository[SharedFile]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "shared_files", SharedFile)

    async def get_by_code(self, code: str) -> SharedFile | None:
        data = await self._col().find_one({"code": code})
        if data is None:
            return None
        return _parse_doc(SharedFile, data)

    async def list_expired(
        self,
        *,
        before: datetime,
        limit: int = 10_000,
    ) -> list[SharedFile]:
        """Return shares whose expires_at is strictly before ``before``."""
        cursor = (
            self._col()
            .find({"expires_at": {"$lt": before}})
            .sort("expires_at", 1)
            .limit(limit)
        )
        return [_parse_doc(SharedFile, row) async for row in cursor]
