"""Mongo repository for admin-saved QR codes."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.qr_code import QrCode
from app.db.repositories.base import MongoRepository


class QrCodeRepository(MongoRepository[QrCode]):
    """CRUD for ``qr_codes`` collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "qr_codes", QrCode)

    async def delete_for_created_by(self, user_id: int) -> int:
        """Delete all QR codes owned by the given user."""
        result = await self._col().delete_many({"created_by": user_id})
        return int(result.deleted_count)
