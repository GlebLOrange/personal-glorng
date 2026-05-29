"""Tests for platform registry and audit trail."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.audit_event import (
    AuditActorType,
    AuditCategory,
    AuditEvent,
    AuditSource,
)
from app.services.audit import AuditRecord, AuditService
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD


@pytest.mark.asyncio
async def test_platform_services_catalog(client: AsyncClient) -> None:
    resp = await client.get("/api/platform/services")
    assert resp.status_code == 200
    data = resp.json()
    assert "services" in data
    assert "categories" in data
    slugs = {s["slug"] for s in data["services"]}
    assert "tasks" in slugs
    assert "audit" in slugs


@pytest.mark.asyncio
async def test_audit_service_records_event(db: AsyncSession) -> None:
    svc = AuditService(db)
    event = await svc.record(
        AuditRecord(
            category=AuditCategory.SECURITY,
            action="auth.login_success",
            actor_type=AuditActorType.USER,
            actor_id=1,
            source=AuditSource.PUBLIC,
            resource_type="user",
            resource_id=1,
        ),
    )
    await db.commit()

    result = await db.execute(select(AuditEvent).where(AuditEvent.id == event.id))
    row = result.scalar_one()
    assert row.action == "auth.login_success"
    assert row.category == "security"


@pytest.mark.asyncio
async def test_audit_list_requires_admin(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/audit")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_audit_list_admin(
    auth_client: AsyncClient,
    db: AsyncSession,
) -> None:
    svc = AuditService(db)
    await svc.record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="recipe.created",
            actor_type=AuditActorType.USER,
            actor_id=1,
            source=AuditSource.WEB_ADMIN,
            resource_type="recipe",
            resource_id=42,
        ),
    )
    await db.commit()

    resp = await auth_client.get("/api/tools/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(i["action"] == "recipe.created" for i in data["items"])


@pytest.mark.asyncio
async def test_login_emits_security_audit(
    client: AsyncClient,
    db: AsyncSession,
    admin_user: object,
) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200

    result = await db.execute(
        select(AuditEvent).where(AuditEvent.action == "auth.login_success"),
    )
    assert result.scalar_one_or_none() is not None
