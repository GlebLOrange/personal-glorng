"""CLI entry: python -m app.db.mongo.migrate"""

import asyncio

from app.db.mongo.client import connect_mongodb, disconnect_mongodb
from app.db.mongo.migrate import ensure_mongo_schema
from app.settings import get_settings


async def main() -> None:
    settings = get_settings()
    if not settings.enable_mongodb():
        return
    client, db = await connect_mongodb(settings.MONGODB_URL, settings.MONGODB_DB)
    try:
        await ensure_mongo_schema(db)
    finally:
        await disconnect_mongodb(client)


if __name__ == "__main__":
    asyncio.run(main())
