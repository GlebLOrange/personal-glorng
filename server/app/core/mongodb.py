"""Backward-compatible MongoDB accessors (prefer DatabaseRegistry)."""

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_registry_db: AsyncIOMotorDatabase | None = None
_registry_client: AsyncIOMotorClient | None = None


def bind_mongodb(
    client: AsyncIOMotorClient,
    database: AsyncIOMotorDatabase,
) -> None:
    """Register the active MongoDB connection for legacy helpers."""
    global _registry_client, _registry_db
    _registry_client = client
    _registry_db = database


def clear_mongodb() -> None:
    global _registry_client, _registry_db
    _registry_client = None
    _registry_db = None


def is_mongodb_enabled() -> bool:
    return _registry_db is not None and _registry_client is not None


def get_mongodb_client() -> AsyncIOMotorClient:
    if _registry_client is None:
        msg = "MongoDB not initialized"
        raise RuntimeError(msg)
    return _registry_client


def get_mongodb_database() -> AsyncIOMotorDatabase:
    if _registry_db is None:
        msg = "MongoDB not initialized"
        raise RuntimeError(msg)
    return _registry_db
