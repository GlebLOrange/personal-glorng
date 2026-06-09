"""Apply MongoDB indexes and schema version tracking."""

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.logging import logger
from app.db.mongo.indexes import INDEX_SPECS
from app.settings import get_settings

_SCHEMA_VERSION = "v001_initial_indexes"

_APP_LOGS_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["id", "occurred_at", "level", "message", "logger", "service"],
        "properties": {
            "id": {"bsonType": "int"},
            "occurred_at": {"bsonType": "date"},
            "level": {
                "bsonType": "string",
                "enum": ["debug", "info", "warning", "error", "critical"],
            },
            "message": {"bsonType": "string", "maxLength": 4096},
            "logger": {"bsonType": "string"},
            "service": {"bsonType": "string"},
            "context": {"bsonType": ["object", "null"]},
            "error": {"bsonType": ["string", "null"]},
            "error_type": {"bsonType": ["string", "null"]},
            "traceback": {"bsonType": ["string", "null"], "maxLength": 8192},
            "request_id": {"bsonType": ["string", "null"]},
        },
        "additionalProperties": False,
    },
}


async def _ensure_app_logs_validator(db: AsyncIOMotorDatabase) -> None:
    """Apply JSON schema validation on app_logs collection."""
    collections = await db.list_collection_names()
    if "app_logs" not in collections:
        await db.create_collection(
            "app_logs",
            validator=_APP_LOGS_VALIDATOR,
            validationLevel="moderate",
            validationAction="error",
        )
        return
    await db.command(
        "collMod",
        "app_logs",
        validator=_APP_LOGS_VALIDATOR,
        validationLevel="moderate",
        validationAction="error",
    )


async def ensure_mongo_schema(db: AsyncIOMotorDatabase) -> None:
    """Create indexes idempotently and record schema version."""
    for collection, keys, options in INDEX_SPECS:
        kwargs = options or {}
        await db[collection].create_index(keys, **kwargs)

    await _ensure_app_logs_validator(db)

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
