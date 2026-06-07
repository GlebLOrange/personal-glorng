import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_expenses_reject_invalid_month(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/expenses", params={"month": "2025-13"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_expenses_reject_inverted_date_range(auth_client: AsyncClient) -> None:
    resp = await auth_client.get(
        "/api/tools/expenses",
        params={"date_from": "2025-06-30", "date_to": "2025-06-01"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_audit_reject_inverted_date_range(auth_client: AsyncClient) -> None:
    resp = await auth_client.get(
        "/api/tools/audit",
        params={"date_from": "2025-06-30", "date_to": "2025-06-01"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_task_rejects_invalid_scheduled_at(
    auth_client: AsyncClient,
) -> None:
    resp = await auth_client.post(
        "/api/tools/tasks",
        json={"title": "Bad time", "scheduled_at": "not-a-datetime"},
    )
    assert resp.status_code == 422
