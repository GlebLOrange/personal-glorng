import re
import uuid
from typing import Any, Literal

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.permissions import SUPERUSER_PERMISSION
from app.core.utils import DEFAULT_PER_PAGE
from app.db.documents.user import User
from app.db.repositories.base import MongoRepository, _parse_doc

RoleFilter = Literal["all", "superuser", "custom"]
StatusFilter = Literal["all", "verified", "unverified", "protected"]


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
        data = await self._col().find_one({"public_id": str(uid)})
        if data is None:
            return None
        return _parse_doc(User, data)

    async def list_all(self) -> list[User]:
        cursor = self._col().find().sort("created_at", 1)
        return [_parse_doc(User, row) async for row in cursor]

    def _admin_list_query(
        self,
        *,
        search: str | None = None,
        role: RoleFilter = "all",
        status: StatusFilter = "all",
    ) -> dict[str, Any]:
        query: dict[str, Any] = {}
        if search:
            pattern = {"$regex": re.escape(search.strip()), "$options": "i"}
            query["$or"] = [{"email": pattern}, {"display_name": pattern}]

        if role == "superuser":
            query["permissions"] = SUPERUSER_PERMISSION
        elif role == "custom":
            query["permissions"] = {"$nin": [SUPERUSER_PERMISSION]}
        if status == "verified":
            query["is_verified"] = True
        elif status == "unverified":
            query["is_verified"] = False
        elif status == "protected":
            query["is_protected"] = True
        return query

    async def list_admin(
        self,
        *,
        offset: int = 0,
        limit: int = DEFAULT_PER_PAGE,
        search: str | None = None,
        role: RoleFilter = "all",
        status: StatusFilter = "all",
    ) -> list[User]:
        query = self._admin_list_query(search=search, role=role, status=status)
        cursor = self._col().find(query).sort("created_at", 1).skip(offset).limit(limit)
        return [_parse_doc(User, row) async for row in cursor]

    async def count_admin(
        self,
        *,
        search: str | None = None,
        role: RoleFilter = "all",
        status: StatusFilter = "all",
    ) -> int:
        query = self._admin_list_query(search=search, role=role, status=status)
        return await self._col().count_documents(query)

    async def admin_stats(self) -> dict[str, int]:
        total = await self._col().count_documents({})
        superuser_count = await self.count_superusers(SUPERUSER_PERMISSION)
        protected_count = await self._col().count_documents({"is_protected": True})
        unverified_count = await self._col().count_documents({"is_verified": False})
        return {
            "total": total,
            "superuser_count": superuser_count,
            "protected_count": protected_count,
            "unverified_count": unverified_count,
        }

    async def count_superusers(self, permission: str) -> int:
        return await self._col().count_documents({"permissions": permission})
