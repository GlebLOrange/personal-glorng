"""MongoDB client lifecycle helpers."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.logging import logger


async def connect_mongodb(url: str, database_name: str) -> tuple[AsyncIOMotorClient, AsyncIOMotorDatabase]:
    """Open a Motor client and verify connectivity."""
    client = AsyncIOMotorClient(url)
    database = client[database_name]
    await client.admin.command("ping")
    logger.info("MongoDB connected", context={"database": database_name})
    return client, database


async def disconnect_mongodb(client: AsyncIOMotorClient | None) -> None:
    """Close the Motor client if open."""
    if client is not None:
        client.close()
