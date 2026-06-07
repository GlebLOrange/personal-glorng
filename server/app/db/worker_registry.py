"""Shared DatabaseRegistry for workers and Telegram bot (outside FastAPI)."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.settings import get_settings

_registry: DatabaseRegistry | None = None


async def get_worker_registry() -> DatabaseRegistry:
    """Return a process-wide initialized registry for background jobs."""
    global _registry
    if _registry is None:
        settings = get_settings()
        registry = DatabaseRegistry()
        init_svc = DatabaseInitService(registry, settings)
        await init_svc.startup()
        _registry = registry
    return _registry


@asynccontextmanager
async def worker_registry() -> AsyncGenerator[DatabaseRegistry]:
    """Yield the shared worker registry."""
    yield await get_worker_registry()
