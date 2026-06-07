from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.logging import logger

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None
_enabled = False


async def init_mongodb(url: str, database_name: str) -> None:
    """Connect to MongoDB when a URL is configured."""
    global _client, _database, _enabled
    if not url.strip():
        return

    _client = AsyncIOMotorClient(url)
    _database = _client[database_name]
    await _client.admin.command("ping")
    _enabled = True
    logger.info(
        "MongoDB connected",
        context={"database": database_name},
    )


async def close_mongodb() -> None:
    global _client, _database, _enabled
    if _client is not None:
        _client.close()
        _client = None
    _database = None
    _enabled = False


def is_mongodb_enabled() -> bool:
    return _enabled and _client is not None and _database is not None


def get_mongodb_client() -> AsyncIOMotorClient:
    if _client is None:
        msg = "MongoDB not initialized. Call init_mongodb() first."
        raise RuntimeError(msg)
    return _client


def get_mongodb_database() -> AsyncIOMotorDatabase:
    if _database is None:
        msg = "MongoDB not initialized. Call init_mongodb() first."
        raise RuntimeError(msg)
    return _database
