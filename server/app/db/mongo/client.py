"""MongoDB client lifecycle helpers."""

from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.logging import logger


async def connect_mongodb(
    url: str,
    database_name: str,
    **client_kwargs: Any,
) -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """Open a Motor client and verify connectivity.

    Pass pool/timeout kwargs from ``Settings.mongodb_client_kwargs()``.
    Defaults omit driver overrides when callers pass nothing (tests/scripts).
    """
    # Local lite: keep maxPoolSize small — several processes share one Mongo.
    client = AsyncIOMotorClient(url, **client_kwargs)
    database = client[database_name]
    await client.admin.command("ping")
    logger.info("MongoDB connected", context={"database": database_name})
    return client, database


async def disconnect_mongodb(client: AsyncIOMotorClient | None) -> None:
    """Close the Motor client if open."""
    if client is not None:
        client.close()
