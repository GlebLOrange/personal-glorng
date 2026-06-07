"""Tests for platform registry and audit trail."""

import pytest
from httpx import AsyncClient

from app.db.documents.audit import (
    AuditActorType,
    AuditCategory,
    AuditSource,
)
from app.db.registry import DatabaseRegistry
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
    assert "ai-chat" not in slugs


@pytest.mark.asyncio
async def test_audit_service_records_event(registry: DatabaseRegistry) -> None:
    svc = AuditService(registry)
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

    row = await registry.mongo_db.audit_events.find_one({"id": event.id})
    assert row is not None
    assert row["action"] == "auth.login_success"
    assert row["category"] == "security"


@pytest.mark.asyncio
async def test_audit_list_requires_admin(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/audit")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_audit_list_admin(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    svc = AuditService(registry)
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

    resp = await auth_client.get("/api/tools/audit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(i["action"] == "recipe.created" for i in data["items"])


@pytest.mark.asyncio
async def test_login_emits_security_audit(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200

    row = await registry.mongo_db.audit_events.find_one(
        {"action": "auth.login_success"},
    )
    assert row is not None
