import pytest
from httpx import AsyncClient

from app.db.documents.app_log import AppLog
from app.db.registry import DatabaseRegistry


@pytest.mark.asyncio
async def test_app_logs_list_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/app-logs")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_app_logs_list_admin(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(id=0, level="info", message="Request completed", logger="glorng"),
            AppLog(id=0, level="error", message="Unhandled failure", logger="glorng"),
        ],
    )

    resp = await auth_client.get("/api/tools/app-logs", params={"level": "error"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["message"] == "Unhandled failure"


@pytest.mark.asyncio
async def test_app_logs_filter_by_message_substring(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(id=0, level="info", message="Recipe created", logger="glorng"),
            AppLog(id=0, level="info", message="Task created", logger="glorng"),
        ],
    )

    resp = await auth_client.get("/api/tools/app-logs", params={"message": "recipe"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["message"] == "Recipe created"
