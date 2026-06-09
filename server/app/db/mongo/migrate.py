"""Apply MongoDB indexes and schema version tracking."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import logger
from app.db.mongo.indexes import INDEX_SPECS
from app.settings import get_settings

_SCHEMA_VERSION = "v001_initial_indexes"


async def ensure_mongo_schema(db: AsyncIOMotorDatabase) -> None:
    """Create indexes idempotently and record schema version."""
    for collection, keys, options in INDEX_SPECS:
        kwargs = options or {}
        await db[collection].create_index(keys, **kwargs)

    settings = get_settings()
    ttl_seconds = settings.APP_LOG_RETENTION_DAYS * 86_400
    await db.app_logs.create_index(
        [("occurred_at", 1)],
        expireAfterSeconds=ttl_seconds,
        name="app_logs_occurred_at_ttl",
    )
    await db.schema_migrations.update_one(
        {"_id": _SCHEMA_VERSION},
        {"$set": {"applied": True}},
        upsert=True,
    )
    logger.info("MongoDB schema ensured", context={"version": _SCHEMA_VERSION})
