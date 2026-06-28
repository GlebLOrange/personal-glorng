"""HTTP-level CSRF checks through RequestIdMiddleware."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, create_refresh_token
from app.settings import get_settings
from tests.env_helpers import ENV_SCENARIOS_DIR, activate_env_file
from tests.factories import create_user


def _enable_production(monkeypatch: pytest.MonkeyPatch) -> None:
    activate_env_file(monkeypatch, ENV_SCENARIOS_DIR / "production-csrf.env")


@pytest.mark.asyncio
@pytest.mark.e2e_api
async def test_csrf_rejects_cookie_post_without_origin(
    client: AsyncClient,
    registry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    user = await create_user(registry, email="csrf@glorng.dev")
    token = create_access_token(str(user.public_id), user_id=user.id)

    resp = await client.post(
        "/api/tools/tasks",
        json={"title": "Blocked", "scheduled_at": "2026-06-01T10:00:00"},
        cookies={"access_token": token},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Origin not allowed"
    assert "x-request-id" in resp.headers
    get_settings.cache_clear()


@pytest.mark.asyncio
@pytest.mark.e2e_api
async def test_csrf_allows_cookie_post_with_allowed_origin(
    client: AsyncClient,
    registry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    user = await create_user(registry, email="csrf-allowed@glorng.dev")
    token = create_access_token(str(user.public_id), user_id=user.id)
    origin = get_settings().CORS_ORIGINS[0]

    resp = await client.post(
        "/api/tools/tasks",
        json={"title": "Allowed", "scheduled_at": "2026-06-01T10:00:00"},
        cookies={"access_token": token},
        headers={"origin": origin},
    )
    assert resp.status_code != 403
    get_settings.cache_clear()


@pytest.mark.asyncio
@pytest.mark.e2e_api
async def test_csrf_rejects_cookie_refresh_without_origin(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)

    resp = await client.post(
        "/api/auth/refresh",
        cookies={"refresh_token": "cookie-refresh-token"},
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Origin not allowed"
    get_settings.cache_clear()


@pytest.mark.asyncio
@pytest.mark.e2e_api
async def test_csrf_allows_body_refresh_without_cookie_origin(
    client: AsyncClient,
    registry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_production(monkeypatch)
    user = await create_user(registry, email="csrf-refresh@glorng.dev")
    refresh_token = create_refresh_token(str(user.public_id))

    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()
    get_settings.cache_clear()
