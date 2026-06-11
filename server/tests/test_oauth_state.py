from __future__ import annotations

from urllib.parse import parse_qs, urlparse

import pytest
from httpx import AsyncClient

from app.core.google_oauth_state import (
    generate_google_oauth_state,
    store_google_oauth_state,
)
from app.db.registry import DatabaseRegistry


@pytest.mark.asyncio
async def test_github_oauth_rejects_state_mismatch(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/auth/github/authorize", follow_redirects=False)
    assert resp.status_code in {302, 307}

    redirect = resp.headers["location"]
    parsed = urlparse(redirect)
    qs = parse_qs(parsed.query)
    assert qs.get("state")

    wrong_state = "definitely-not-the-same-state"
    callback = await auth_client.post(
        "/api/auth/github/callback",
        json={"code": "dummy", "state": wrong_state},
    )
    assert callback.status_code == 401


@pytest.mark.asyncio
async def test_github_oauth_state_is_one_time_use(
    auth_client: AsyncClient,
    registry: DatabaseRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.routers import github as github_router

    async def fake_exchange_code_for_token(code: str) -> str:
        assert code == "dummy"
        return "gh-token"

    async def fake_get_github_user(access_token: str) -> dict:
        assert access_token == "gh-token"
        return {"login": "allowed-user", "id": 123}

    def fake_validate_allowed_user(username: str) -> None:
        # The allowlist is config-driven; keep this test isolated from env.
        assert username

    monkeypatch.setattr(
        github_router, "exchange_code_for_token", fake_exchange_code_for_token
    )
    monkeypatch.setattr(github_router, "get_github_user", fake_get_github_user)
    monkeypatch.setattr(
        github_router, "validate_allowed_user", fake_validate_allowed_user
    )

    resp = await auth_client.get("/api/auth/github/authorize", follow_redirects=False)
    assert resp.status_code in {302, 307}

    redirect = resp.headers["location"]
    parsed = urlparse(redirect)
    qs = parse_qs(parsed.query)
    state = qs["state"][0]

    first = await auth_client.post(
        "/api/auth/github/callback",
        json={"code": "dummy", "state": state},
    )
    assert first.status_code == 200

    credential = await registry.mongo_db.github_credentials.find_one(
        {"github_username": "allowed-user"},
    )
    assert credential is not None
    assert credential["access_token"].startswith("enc:")

    second = await auth_client.post(
        "/api/auth/github/callback",
        json={"code": "dummy", "state": state},
    )
    assert second.status_code == 401


@pytest.mark.asyncio
async def test_google_oauth_rejects_unknown_state(client: AsyncClient) -> None:
    resp = await client.get(
        "/api/callbacks/google",
        params={"code": "dummy", "state": "unknown-state-token"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_google_oauth_state_is_one_time_use(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import AsyncMock, MagicMock

    from app.routers import callbacks as callbacks_router

    state = generate_google_oauth_state()
    await store_google_oauth_state(state=state, telegram_user_id=123)

    mock_creds = MagicMock()
    mock_creds.refresh_token = "new-refresh-token"
    mock_flow = MagicMock()
    mock_flow.credentials = mock_creds

    monkeypatch.setattr(
        callbacks_router.Flow,
        "from_client_config",
        MagicMock(return_value=mock_flow),
    )
    monkeypatch.setattr(callbacks_router, "Bot", MagicMock(return_value=AsyncMock()))

    first = await client.get(
        "/api/callbacks/google",
        params={"code": "auth-code", "state": state},
    )
    assert first.status_code == 200

    second = await client.get(
        "/api/callbacks/google",
        params={"code": "auth-code", "state": state},
    )
    assert second.status_code == 400
