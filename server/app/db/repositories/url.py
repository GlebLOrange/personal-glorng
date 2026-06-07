from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.url import ShortenedUrl
from app.db.repositories.base import MongoRepository, _parse_doc


class UrlRepository(MongoRepository[ShortenedUrl]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "shortened_urls", ShortenedUrl)

    async def get_by_code(self, code: str) -> ShortenedUrl | None:
        data = await self._col().find_one({"code": code})
        if data is None:
            return None
        return _parse_doc(ShortenedUrl, data)
