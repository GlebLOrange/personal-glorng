import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.documents.task import TaskStatus
from app.db.registry import DatabaseRegistry
from app.services.task import complete_past_due_tasks
from app.settings import get_settings
from tests.factories import create_task, create_user


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
async def test_create_task_sanitizes_description_and_location(
    auth_client: AsyncClient,
) -> None:
    resp = await auth_client.post(
        "/api/tools/tasks",
        json={
            "title": "Errand",
            "scheduled_at": "2026-06-01T10:00:00",
            "description": "  pick\x00 up  ",
            "location": f"  shop\x00 {'x' * 240}",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "pick up"
    assert data["location"].startswith("shop ")
    assert len(data["location"]) <= 255


@pytest.mark.asyncio
async def test_create_task_rejects_empty_title_after_sanitize(
    auth_client: AsyncClient,
) -> None:
    resp = await auth_client.post(
        "/api/tools/tasks",
        json={
            "title": "   \x00  ",
            "scheduled_at": "2026-06-01T10:00:00",
        },
    )
    assert resp.status_code == 422


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


@pytest.fixture
async def tasks_reader_client(
    client: AsyncClient, registry: DatabaseRegistry
) -> AsyncClient:
    user = await create_user(
        registry,
        email="reader@example.com",
        permissions=["tasks:read", "tasks:write"],
    )
    token = create_access_token(str(user.public_id))
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.mark.asyncio
async def test_task_mutations_require_superuser(
    tasks_reader_client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    task = await create_task(registry)

    create_resp = await tasks_reader_client.post(
        "/api/tools/tasks",
        json={"title": "Denied", "scheduled_at": "2026-06-01T10:00:00"},
    )
    assert create_resp.status_code == 403

    status_resp = await tasks_reader_client.patch(
        f"/api/tools/tasks/{task.id}/status",
        json={"status": "completed"},
    )
    assert status_resp.status_code == 403

    reschedule_resp = await tasks_reader_client.patch(
        f"/api/tools/tasks/{task.id}",
        json={"scheduled_at": "2026-06-02T10:00:00"},
    )
    assert reschedule_resp.status_code == 403

    reminder_resp = await tasks_reader_client.post(
        f"/api/tools/tasks/{task.id}/reminders",
        json={"minutes_before": 15},
    )
    assert reminder_resp.status_code == 403

    retry_resp = await tasks_reader_client.post(
        f"/api/tools/tasks/{task.id}/retry-sync",
    )
    assert retry_resp.status_code == 403


@pytest.mark.asyncio
async def test_tasks_reader_can_list(
    registry: DatabaseRegistry,
    tasks_reader_client: AsyncClient,
) -> None:
    await create_task(registry, title="Visible task")
    resp = await tasks_reader_client.get("/api/tools/tasks")
    assert resp.status_code == 200
    assert any(t["title"] == "Visible task" for t in resp.json())


@pytest.mark.asyncio
async def test_complete_past_due_tasks(registry: DatabaseRegistry) -> None:
    from datetime import UTC, datetime, timedelta

    future = await create_task(
        registry,
        title="Future",
        scheduled_at=datetime.now(UTC) + timedelta(hours=1),
    )
    past = await create_task(
        registry,
        title="Past",
        scheduled_at=datetime.now(UTC) - timedelta(minutes=5),
    )

    count = await complete_past_due_tasks(registry)
    assert registry.tasks is not None
    past = await registry.tasks.get(past.id)
    future = await registry.tasks.get(future.id)

    assert count == 1
    assert past.status == TaskStatus.COMPLETED
    assert future.status == TaskStatus.PENDING
