"""API tests for the health-checker tool."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.documents.health_checker import DnsRecord
from app.db.registry import DatabaseRegistry
from app.services.health_checker import ProbeOutcome
from tests.factories import create_user


def _ok_outcome() -> ProbeOutcome:
    return ProbeOutcome(
        status_code=200,
        response_ms=42.5,
        ok=True,
        error=None,
        ssl_expires_at=datetime(2027, 1, 1, tzinfo=UTC),
        dns=[DnsRecord(family="A", address="93.184.216.34")],
    )


@pytest.mark.asyncio
async def test_list_monitors_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/health-checker")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_monitor(
    auth_client: AsyncClient,
) -> None:
    with patch(
        "app.services.health_checker.is_public_http_url",
        return_value=True,
    ), patch(
        "app.services.health_checker.probe_url",
        new=AsyncMock(return_value=_ok_outcome()),
    ):
        resp = await auth_client.post(
            "/api/tools/health-checker",
            json={
                "url": "https://example.com",
                "label": "Example",
                "interval_minutes": 5,
            },
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["url"] == "https://example.com/"
    assert data["label"] == "Example"
    assert data["last_ok"] is True
    assert data["last_status_code"] == 200
    assert data["uptime_percent"] == 100.0
    assert data["dns"][0]["family"] == "A"


@pytest.mark.asyncio
async def test_create_monitor_rejects_private_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/health-checker",
        json={"url": "http://127.0.0.1/secret"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_scoped_to_owner(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    other = await create_user(
        registry,
        email="hc-other@glorng.dev",
        permissions=["health-checker:read", "health-checker:write"],
    )
    with patch(
        "app.services.health_checker.is_public_http_url",
        return_value=True,
    ), patch(
        "app.services.health_checker.probe_url",
        new=AsyncMock(return_value=_ok_outcome()),
    ):
        from app.services.health_checker import HealthMonitorService

        svc = HealthMonitorService(registry)
        await svc.create_monitor(
            url="https://example.com/admin",
            created_by=admin_user.id,  # type: ignore[union-attr]
            label="Admin",
        )
        await svc.create_monitor(
            url="https://example.com/other",
            created_by=other.id,
            label="Other",
        )

    token = create_access_token(str(other.public_id), user_id=other.id)
    resp = await client.get(
        "/api/tools/health-checker",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["label"] == "Other"


@pytest.mark.asyncio
async def test_history_and_check_now(auth_client: AsyncClient) -> None:
    with patch(
        "app.services.health_checker.is_public_http_url",
        return_value=True,
    ), patch(
        "app.services.health_checker.probe_url",
        new=AsyncMock(return_value=_ok_outcome()),
    ):
        create = await auth_client.post(
            "/api/tools/health-checker",
            json={"url": "https://example.com/hist"},
        )
        assert create.status_code == 201
        monitor_id = create.json()["id"]

        history = await auth_client.get(
            f"/api/tools/health-checker/{monitor_id}/history"
        )
        assert history.status_code == 200
        assert len(history.json()["items"]) >= 1

        check = await auth_client.post(
            f"/api/tools/health-checker/{monitor_id}/check"
        )
        assert check.status_code == 200
        assert check.json()["last_ok"] is True


@pytest.mark.asyncio
async def test_other_users_monitor_forbidden(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    other = await create_user(
        registry,
        email="hc-forbid@glorng.dev",
        permissions=["health-checker:read", "health-checker:write"],
    )
    with patch(
        "app.services.health_checker.is_public_http_url",
        return_value=True,
    ), patch(
        "app.services.health_checker.probe_url",
        new=AsyncMock(return_value=_ok_outcome()),
    ):
        from app.services.health_checker import HealthMonitorService

        monitor = await HealthMonitorService(registry).create_monitor(
            url="https://example.com/owned",
            created_by=admin_user.id,  # type: ignore[union-attr]
        )

    token = create_access_token(str(other.public_id), user_id=other.id)
    headers = {"Authorization": f"Bearer {token}"}
    get_resp = await client.get(
        f"/api/tools/health-checker/{monitor.id}",
        headers=headers,
    )
    assert get_resp.status_code == 403

    del_resp = await client.delete(
        f"/api/tools/health-checker/{monitor.id}",
        headers=headers,
    )
    assert del_resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_monitor(auth_client: AsyncClient) -> None:
    with patch(
        "app.services.health_checker.is_public_http_url",
        return_value=True,
    ), patch(
        "app.services.health_checker.probe_url",
        new=AsyncMock(return_value=_ok_outcome()),
    ):
        create = await auth_client.post(
            "/api/tools/health-checker",
            json={"url": "https://example.com/del"},
        )
        monitor_id = create.json()["id"]
        resp = await auth_client.delete(f"/api/tools/health-checker/{monitor_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_capability_required(
    client: AsyncClient,
    registry: DatabaseRegistry,
) -> None:
    user = await create_user(
        registry,
        email="hc-noperm@glorng.dev",
        permissions=[],
    )
    token = create_access_token(str(user.public_id), user_id=user.id)
    resp = await client.get(
        "/api/tools/health-checker",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403
