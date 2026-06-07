from __future__ import annotations

from datetime import timedelta
from urllib.parse import parse_qs, urlparse

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_oauth_state_token
from app.db.models.github_credential import GitHubCredential


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
    db: AsyncSession,
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

    monkeypatch.setattr(github_router, "exchange_code_for_token", fake_exchange_code_for_token)
    monkeypatch.setattr(github_router, "get_github_user", fake_get_github_user)
    monkeypatch.setattr(github_router, "validate_allowed_user", fake_validate_allowed_user)

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

    result = await db.execute(select(GitHubCredential))
    credential = result.scalar_one()
    assert credential.access_token.startswith("enc:")

    second = await auth_client.post(
        "/api/auth/github/callback",
        json={"code": "dummy", "state": state},
    )
    assert second.status_code == 401


@pytest.mark.asyncio
async def test_google_oauth_rejects_non_oauth_state_token(client: AsyncClient) -> None:
    bad_state = create_access_token("123")
    resp = await client.get(
        "/api/callbacks/google",
        params={"code": "dummy", "state": bad_state},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_google_oauth_rejects_expired_state_token(client: AsyncClient) -> None:
    expired = create_oauth_state_token("123", expires_delta=timedelta(seconds=-1))
    resp = await client.get(
        "/api/callbacks/google",
        params={"code": "dummy", "state": expired},
    )
    assert resp.status_code == 400

