"""Centralized database initialization for all enabled backends."""

import asyncio

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.logging import logger
from app.db.mongo.client import connect_mongodb, disconnect_mongodb
from app.db.mongo.migrate import ensure_mongo_schema
from app.db.registry import DatabaseRegistry
from app.settings import Settings


class DatabaseInitService:
    """Initialize and tear down configured database backends."""

    def __init__(self, registry: DatabaseRegistry, settings: Settings) -> None:
        self.registry = registry
        self.settings = settings

    async def startup(self) -> None:
        if self.settings.enable_mongodb():
            await self._init_mongo()
        if self.settings.enable_postgres():
            await self._init_postgres()
        if self.registry.mongo_db is not None:
            self.registry.init_repositories()

    async def shutdown(self) -> None:
        await disconnect_mongodb(self.registry.mongo_client)
        self.registry.mongo_client = None
        self.registry.mongo_db = None

    async def _init_mongo(self) -> None:
        client, database = await connect_mongodb(
            self.settings.MONGODB_URL,
            self.settings.MONGODB_DB,
        )
        self.registry.mongo_client = client
        self.registry.mongo_db = database
        await ensure_mongo_schema(database)

    async def _init_postgres(self) -> None:
        await self._wait_for_postgres()
        engine = create_async_engine(self.settings.DATABASE_URL, echo=False)
        self.registry.postgres_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        if self.settings.RUN_MIGRATIONS:
            await self._run_alembic()
        logger.info("PostgreSQL connected (secondary)")

    async def _wait_for_postgres(self, *, max_attempts: int = 30) -> None:
        engine = create_async_engine(
            self.settings.DATABASE_URL,
            pool_pre_ping=True,
        )
        try:
            for _ in range(max_attempts):
                try:
                    async with engine.connect() as conn:
                        await conn.execute(text("SELECT 1"))
                    return
                except OSError, Exception:
                    await asyncio.sleep(1)
            msg = "PostgreSQL not ready after retries"
            raise RuntimeError(msg)
        finally:
            await engine.dispose()

    async def _run_alembic(self) -> None:
        import subprocess
        from pathlib import Path

        server_root = Path(__file__).resolve().parents[2]
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=server_root,
            check=False,
        )
        if result.returncode != 0:
            msg = "Alembic migration failed"
            raise RuntimeError(msg)
