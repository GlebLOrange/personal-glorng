"""Apply MongoDB indexes and schema version tracking."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import logger
from app.db.mongo.indexes import INDEX_SPECS

_SCHEMA_VERSION = "v001_initial_indexes"


async def ensure_mongo_schema(db: AsyncIOMotorDatabase) -> None:
    """Create indexes idempotently and record schema version."""
    for collection, keys, options in INDEX_SPECS:
        kwargs = options or {}
        await db[collection].create_index(keys, **kwargs)
    await db.schema_migrations.update_one(
        {"_id": _SCHEMA_VERSION},
        {"$set": {"applied": True}},
        upsert=True,
    )
    logger.info("MongoDB schema ensured", context={"version": _SCHEMA_VERSION})
