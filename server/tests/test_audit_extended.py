"""Audit API immutability and filter success paths."""

import pytest
from httpx import AsyncClient

from app.db.documents.audit import AuditActorType, AuditCategory, AuditSource
from app.db.registry import DatabaseRegistry
from app.services.audit import AuditRecord, AuditService


@pytest.mark.asyncio
async def test_audit_api_is_read_only(auth_client: AsyncClient) -> None:
    resp = await auth_client.post("/api/tools/audit", json={})
    assert resp.status_code == 405

    delete_resp = await auth_client.delete("/api/tools/audit")
    assert delete_resp.status_code == 405


@pytest.mark.asyncio
async def test_audit_filter_by_category(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    svc = AuditService(registry)
    await svc.record(
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
    await svc.record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="recipe.created",
            actor_type=AuditActorType.USER,
            actor_id=1,
            source=AuditSource.WEB_ADMIN,
            resource_type="recipe",
            resource_id=99,
        ),
    )

    resp = await auth_client.get("/api/tools/audit", params={"category": "security"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert all(item["category"] == "security" for item in data["items"])


@pytest.mark.asyncio
async def test_audit_filter_by_action(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    svc = AuditService(registry)
    await svc.record(
        AuditRecord(
            category=AuditCategory.DOMAIN,
            action="task.created",
            actor_type=AuditActorType.USER,
            actor_id=1,
            source=AuditSource.WEB_ADMIN,
            resource_type="task",
            resource_id=7,
        ),
    )

    resp = await auth_client.get(
        "/api/tools/audit",
        params={"action": "task.created"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert any(item["action"] == "task.created" for item in data["items"])
