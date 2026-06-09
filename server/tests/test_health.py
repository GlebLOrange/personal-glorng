from httpx import AsyncClient


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
    assert body["checks"]["redis"] == "ok"


async def test_ready_includes_rabbitmq_check(client: AsyncClient) -> None:
    response = await client.get("/api/ready")
    body = response.json()
    assert "rabbitmq" in body["checks"]
    assert body["checks"]["rabbitmq"] in {"ok", "degraded"}


async def test_ready_includes_redis_memory_info(client: AsyncClient) -> None:
    response = await client.get("/api/ready")
    body = response.json()
    assert "redis_memory" in body["checks"]
    assert isinstance(body["checks"]["redis_memory"], dict)
