from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.weather import WeatherLocation
from app.db.repositories.base import MongoRepository


class WeatherRepository(MongoRepository[WeatherLocation]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "weather_locations", WeatherLocation)

    async def list_for_user(self, user_id: int) -> list[WeatherLocation]:
        return await self.list(user_id=user_id, limit=100, sort=[("sort_order", 1)])
