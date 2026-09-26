"""Mongo repository for generated QR codes."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.qr_code import QrCode
from app.db.repositories.base import MongoRepository


class QrCodeRepository(MongoRepository[QrCode]):
    """CRUD for ``qr_codes`` collection."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "qr_codes", QrCode)
