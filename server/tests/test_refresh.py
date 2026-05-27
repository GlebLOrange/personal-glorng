import pytest
from httpx import AsyncClient

from tests.conftest import ADMIN_EMAIL


@pytest.mark.asyncio
async def test_refresh_returns_new_tokens(
    client: AsyncClient,
    login_tokens: dict[str, str],
) -> None:
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    new_tokens = resp.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["access_token"] != login_tokens["access_token"]
    assert new_tokens["refresh_token"] != login_tokens["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_old_token_blacklisted(
    client: AsyncClient,
    login_tokens: dict[str, str],
) -> None:
    old_refresh = login_tokens["refresh_token"]
    await client.post("/api/auth/refresh", json={"refresh_token": old_refresh})

    reuse_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert reuse_resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "not.a.valid.jwt"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_new_access_token_works(
    client: AsyncClient,
    login_tokens: dict[str, str],
) -> None:
    refresh_resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    new_access = refresh_resp.json()["access_token"]

    me_resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {new_access}"},
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == ADMIN_EMAIL
