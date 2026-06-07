from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.recipe import Recipe
from app.db.repositories.base import MongoRepository


class RecipeRepository(MongoRepository[Recipe]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "recipes", Recipe)
