import pytest
from httpx import AsyncClient

from app.settings import get_settings


@pytest.fixture(autouse=True)
def telegram_user_id(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_ALLOWED_USER_ID", "123456789")
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_create_task_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/tasks",
        json={"title": "Buy milk", "scheduled_at": "2026-06-01T10:00:00"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_task_sanitizes_title(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/tasks",
        json={
            "title": "  buy\x00 milk  ",
            "scheduled_at": "2026-06-01T10:00:00",
            "description": "From admin",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "buy milk"


@pytest.mark.asyncio
async def test_create_task(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/tasks",
        json={
            "title": "Buy milk",
            "scheduled_at": "2026-06-01T10:00:00",
            "description": "From admin",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Buy milk"
    assert data["telegram_user_id"] == 123456789
    assert data["status"] == "pending"

    listed = await auth_client.get("/api/tools/tasks")
    assert any(t["id"] == data["id"] for t in listed.json())


@pytest.mark.asyncio
async def test_list_tasks_rejects_invalid_status(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/tasks", params={"status": "bogus"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_task_status(auth_client: AsyncClient) -> None:
    create = await auth_client.post(
        "/api/tools/tasks",
        json={"title": "Status test", "scheduled_at": "2026-06-01T10:00:00"},
    )
    task_id = create.json()["id"]

    resp = await auth_client.patch(
        f"/api/tools/tasks/{task_id}/status",
        json={"status": "completed"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_reschedule_task(auth_client: AsyncClient) -> None:
    create = await auth_client.post(
        "/api/tools/tasks",
        json={"title": "Reschedule test", "scheduled_at": "2026-06-01T10:00:00"},
    )
    task_id = create.json()["id"]

    resp = await auth_client.patch(
        f"/api/tools/tasks/{task_id}",
        json={"scheduled_at": "2026-06-02T14:30:00"},
    )
    assert resp.status_code == 200
    assert "2026-06-02T14:30:00" in resp.json()["scheduled_at"]
