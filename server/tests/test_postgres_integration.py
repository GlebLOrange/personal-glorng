"""Optional Postgres integration tests (skipped unless POSTGRES_TEST_URL is set)."""

import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


@pytest.mark.postgres
@pytest.mark.asyncio
async def test_postgres_connection() -> None:
    database_url = os.environ.get("POSTGRES_TEST_URL")
    if not database_url:
        pytest.skip("POSTGRES_TEST_URL not set")

    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as conn:
            result = await conn.scalar(text("SELECT 1"))
        assert result == 1
    finally:
        await engine.dispose()
