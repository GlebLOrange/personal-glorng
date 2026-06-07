"""FastAPI dependencies for database registry access."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError
from app.db.registry import DatabaseRegistry
from app.settings import Settings, get_settings


def get_registry(request: Request) -> DatabaseRegistry:
    registry: DatabaseRegistry | None = getattr(request.app.state, "db_registry", None)
    if registry is None:
        msg = "Database registry is not initialized"
        raise RuntimeError(msg)
    return registry


DbRegistry = Annotated[DatabaseRegistry, Depends(get_registry)]


async def get_postgres_db(
    registry: DbRegistry,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession]:
    if not settings.enable_postgres():
        raise ApiError(503, "PostgreSQL is not configured")
    factory = registry.require_postgres_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


PostgresSession = Annotated[AsyncSession, Depends(get_postgres_db)]
