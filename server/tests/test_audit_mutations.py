"""Audit events emitted by expense, file-share, and URL mutations."""

import io

import pytest
from httpx import AsyncClient

from app.db.registry import DatabaseRegistry

EXPENSE_DATA = {
    "tool_name": "AuditProbe",
    "amount": "9.99",
    "currency": "USD",
    "expense_date": "2026-03-15",
    "category": "AI",
    "notes": "audit test",
}


def _make_file(name: str = "audit.txt", content: bytes = b"audit") -> dict:
    return {"file": (name, io.BytesIO(content), "text/plain")}


async def _audit_action(registry: DatabaseRegistry, action: str) -> dict | None:
    return await registry.mongo_db.audit_events.find_one({"action": action})


@pytest.mark.asyncio
async def test_expense_create_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    resp = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
    assert resp.status_code == 201
    expense_id = resp.json()["id"]

    row = await _audit_action(registry, "expense.created")
    assert row is not None
    assert row["resource_type"] == "expense"
    assert row["resource_id"] == expense_id


@pytest.mark.asyncio
async def test_expense_update_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    create = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
    expense_id = create.json()["id"]

    resp = await auth_client.put(
        f"/api/tools/expenses/{expense_id}",
        json={"notes": "updated for audit"},
    )
    assert resp.status_code == 200

    row = await _audit_action(registry, "expense.updated")
    assert row is not None
    assert row["resource_id"] == expense_id


@pytest.mark.asyncio
async def test_expense_delete_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    create = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
    expense_id = create.json()["id"]

    resp = await auth_client.delete(f"/api/tools/expenses/{expense_id}")
    assert resp.status_code == 204

    row = await _audit_action(registry, "expense.deleted")
    assert row is not None
    assert row["resource_id"] == expense_id


@pytest.mark.asyncio
async def test_file_upload_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    resp = await auth_client.post("/api/tools/file-share", files=_make_file())
    assert resp.status_code == 201
    file_id = resp.json()["id"]

    row = await _audit_action(registry, "file.uploaded")
    assert row is not None
    assert row["resource_type"] == "file"
    assert row["resource_id"] == file_id


@pytest.mark.asyncio
async def test_file_delete_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    upload = await auth_client.post("/api/tools/file-share", files=_make_file())
    file_id = upload.json()["id"]

    resp = await auth_client.delete(f"/api/tools/file-share/{file_id}")
    assert resp.status_code == 204

    row = await _audit_action(registry, "file.deleted")
    assert row is not None
    assert row["resource_id"] == file_id


@pytest.mark.asyncio
async def test_url_create_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://audit-example.com", "title": "Audit"},
    )
    assert resp.status_code == 201
    url_id = resp.json()["id"]

    row = await _audit_action(registry, "url.created")
    assert row is not None
    assert row["resource_type"] == "url"
    assert row["resource_id"] == url_id


@pytest.mark.asyncio
async def test_url_delete_emits_audit(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    create = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://audit-delete.com"},
    )
    url_id = create.json()["id"]

    resp = await auth_client.delete(f"/api/tools/url-shortener/{url_id}")
    assert resp.status_code == 204

    row = await _audit_action(registry, "url.deleted")
    assert row is not None
    assert row["resource_id"] == url_id
