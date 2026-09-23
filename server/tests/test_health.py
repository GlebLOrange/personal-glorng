from typing import Any
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.routers import health as health_router


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_ready_returns_dependency_checks(client: AsyncClient) -> None:
    response = await client.get("/api/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["mongodb"] == "ok"
    assert body["checks"]["redis"] in {"ok", "warn"}
    memory = body["checks"]["redis_memory"]
    assert set(memory) >= {"used_memory", "maxmemory", "maxmemory_policy"}
    assert isinstance(memory["used_memory"], int)
    assert isinstance(memory["maxmemory"], int)
    assert isinstance(memory["maxmemory_policy"], str)


async def test_ready_includes_rabbitmq_check(client: AsyncClient) -> None:
    response = await client.get("/api/ready")
    body = response.json()
    assert "rabbitmq" in body["checks"]
    assert body["checks"]["rabbitmq"] in {"ok", "degraded"}


@pytest.mark.asyncio
async def test_check_redis_warns_when_memory_above_85_percent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    redis_client = AsyncMock()
    redis_client.ping = AsyncMock(return_value=True)
    monkeypatch.setattr(health_router, "get_redis_client", lambda: redis_client)

    async def _high_usage() -> dict[str, Any]:
        return {
            "used_memory": 90,
            "maxmemory": 100,
            "maxmemory_policy": "noeviction",
            "warning": "memory_above_85_percent",
        }

    monkeypatch.setattr(health_router, "get_redis_memory_info", _high_usage)

    status, memory = await health_router._check_redis()
    assert status == "warn"
    assert memory == {
        "used_memory": 90,
        "maxmemory": 100,
        "maxmemory_policy": "noeviction",
    }
