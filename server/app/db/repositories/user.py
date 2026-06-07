import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.user import User
from app.db.repositories.base import MongoRepository, _parse_doc


class UserRepository(MongoRepository[User]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "users", User)

    async def get_by_email(self, email: str) -> User | None:
        data = await self._col().find_one({"email": email.strip().lower()})
        if data is None:
            return None
        return _parse_doc(User, data)

    async def get_by_public_id(self, public_id: str | uuid.UUID) -> User | None:
        try:
            uid = (
                public_id
                if isinstance(public_id, uuid.UUID)
                else uuid.UUID(str(public_id))
            )
        except ValueError:
            return None
        data = await self._col().find_one({"public_id": uid})
        if data is None:
            return None
        return _parse_doc(User, data)

    async def list_all(self) -> list[User]:
        cursor = self._col().find().sort("created_at", 1)
        return [_parse_doc(User, row) async for row in cursor]

    async def count_superusers(self, permission: str) -> int:
        count = 0
        cursor = self._col().find({"permissions": permission})
        async for _ in cursor:
            count += 1
        return count
