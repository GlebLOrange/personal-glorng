"""Postgres integration tests (P1 — requires POSTGRES_TEST_URL and migrations)."""

import os

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.documents.search import SearchVisibility
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService
from app.services.search_index import SearchIndexService
from app.services.search_types import SearchDocumentInput
from app.settings import get_settings


def _postgres_url() -> str | None:
    return os.environ.get("POSTGRES_TEST_URL")


@pytest.fixture
async def postgres_session() -> AsyncSession:
    database_url = _postgres_url()
    if not database_url:
        pytest.skip("POSTGRES_TEST_URL not set")

    engine = create_async_engine(database_url)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()


@pytest.mark.postgres
@pytest.mark.asyncio
async def test_postgres_connection() -> None:
    database_url = _postgres_url()
    if not database_url:
        pytest.skip("POSTGRES_TEST_URL not set")

    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as conn:
            result = await conn.scalar(text("SELECT 1"))
        assert result == 1
    finally:
        await engine.dispose()


@pytest.mark.postgres
@pytest.mark.asyncio
async def test_audit_dual_write_postgres(
    registry: DatabaseRegistry,
    postgres_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_POSTGRES", "true")
    get_settings.cache_clear()

    svc = AuditService(registry, postgres_db=postgres_session)
    await svc.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.password_reset_completed",
            actor_type=AuditActorType.USER,
            actor_id=1,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=1,
        ),
    )
    await postgres_session.commit()

    from app.db.models.audit_event import AuditEvent as PgAuditEvent

    result = await postgres_session.execute(
        select(PgAuditEvent).where(
            PgAuditEvent.action == "auth.password_reset_completed",
        ),
    )
    row = result.scalar_one_or_none()
    assert row is not None
    assert row.category == "security"
    get_settings.cache_clear()


@pytest.mark.postgres
@pytest.mark.asyncio
async def test_search_upsert_and_query_postgres(
    registry: DatabaseRegistry,
    postgres_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENABLE_POSTGRES", "true")
    get_settings.cache_clear()

    unique_token = "pgsearchtoken9876"
    svc = SearchIndexService(registry, postgres_db=postgres_session)
    await svc.upsert(
        SearchDocumentInput(
            source_type="resume",
            source_id=9999,
            title="Postgres search probe",
            body=f"Unique searchable body {unique_token}",
            url="/",
            visibility=SearchVisibility.PUBLIC,
        ),
    )
    await postgres_session.commit()

    hits = await svc.search(
        unique_token,
        visibilities=[SearchVisibility.PUBLIC],
        source_types=["resume"],
    )
    assert any(unique_token in hit.body for hit in hits)
    get_settings.cache_clear()
