from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.feedback import Feedback
from app.db.repositories.base import MongoRepository


class FeedbackRepository(MongoRepository[Feedback]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "feedback", Feedback)
