from datetime import UTC, datetime

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


@pytest.mark.asyncio
async def test_app_logs_filter_by_request_id(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(
                id=0,
                level="info",
                message="Matched request",
                logger="glorng",
                request_id="req-abc-123",
            ),
            AppLog(
                id=0,
                level="info",
                message="Other request",
                logger="glorng",
                request_id="req-xyz-999",
            ),
        ],
    )

    resp = await auth_client.get(
        "/api/tools/app-logs",
        params={"request_id": "req-abc-123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["request_id"] == "req-abc-123"


@pytest.mark.asyncio
async def test_app_logs_filter_by_date_range(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(
                id=0,
                level="info",
                message="March log",
                logger="glorng",
                occurred_at=datetime(2026, 3, 10, 12, 0, tzinfo=UTC),
            ),
            AppLog(
                id=0,
                level="info",
                message="June log",
                logger="glorng",
                occurred_at=datetime(2026, 6, 10, 12, 0, tzinfo=UTC),
            ),
        ],
    )

    resp = await auth_client.get(
        "/api/tools/app-logs",
        params={"date_from": "2026-06-01", "date_to": "2026-06-30"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["message"] == "June log"


@pytest.mark.asyncio
async def test_app_logs_pagination(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    assert registry.app_logs is not None
    await registry.app_logs.insert_many(
        [
            AppLog(id=0, level="info", message=f"Log {index}", logger="glorng")
            for index in range(3)
        ],
    )

    page_one = await auth_client.get(
        "/api/tools/app-logs",
        params={"page": 1, "per_page": 2},
    )
    assert page_one.status_code == 200
    first = page_one.json()
    assert first["total"] == 3
    assert len(first["items"]) == 2

    page_two = await auth_client.get(
        "/api/tools/app-logs",
        params={"page": 2, "per_page": 2},
    )
    assert page_two.status_code == 200
    second = page_two.json()
    assert len(second["items"]) == 1
