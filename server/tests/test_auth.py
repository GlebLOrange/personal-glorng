from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.core.security import create_verification_token
from app.settings import get_settings
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD

# --- Registration ---


@pytest.mark.asyncio
async def test_register_allowed_email(client: AsyncClient) -> None:
    settings = get_settings()
    resp = await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    assert resp.status_code == 200
    assert "Registration successful" in resp.json()["message"]


@pytest.mark.asyncio
async def test_register_forbidden_email(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={"email": "hacker@evil.com", "password": "hackerpass1"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, admin_user: object) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={"email": ADMIN_EMAIL, "password": "securepass123"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    settings = get_settings()
    resp = await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "short"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_no_digit_password(client: AsyncClient) -> None:
    settings = get_settings()
    resp = await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "nopdigithere"},
    )
    assert resp.status_code == 422


# --- Login ---


@pytest.mark.asyncio
async def test_login_unverified(client: AsyncClient) -> None:
    settings = get_settings()
    await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_login_verified(client: AsyncClient, admin_user: object) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user: object) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": "wrongpassword1"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@glorng.dev", "password": "somepass123"},
    )
    assert resp.status_code == 401


# --- Me ---


@pytest.mark.asyncio
async def test_me_unauthorized(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == ADMIN_EMAIL
    assert data["is_admin"] is True
    assert data["is_verified"] is True


# --- Token Refresh ---


@pytest.mark.asyncio
async def test_refresh_token(
    client: AsyncClient, login_tokens: dict[str, str]
) -> None:
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": "garbage.token.value"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_reuse_prevented(
    client: AsyncClient, login_tokens: dict[str, str]
) -> None:
    """After refreshing, the old refresh token should be blacklisted."""
    await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    resp = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert resp.status_code == 401


# --- Logout ---


@pytest.mark.asyncio
async def test_logout(
    client: AsyncClient,
    login_tokens: dict[str, str],
) -> None:
    access = login_tokens["access_token"]
    resp = await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
        json={"refresh_token": login_tokens["refresh_token"]},
    )
    assert resp.status_code == 200
    assert "Logged out" in resp.json()["message"]


@pytest.mark.asyncio
async def test_access_after_logout(
    client: AsyncClient,
    login_tokens: dict[str, str],
) -> None:
    """Access token should be blacklisted after logout."""
    access = login_tokens["access_token"]
    await client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access}"},
    )
    resp = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access}"},
    )
    assert resp.status_code == 401


# --- Email Verification ---


@pytest.mark.asyncio
async def test_verify_email(client: AsyncClient) -> None:
    settings = get_settings()
    await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    token = create_verification_token(settings.ALLOWED_EMAIL)
    resp = await client.get(f"/api/auth/verify?token={token}")
    assert resp.status_code == 200
    assert "verified" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_verify_invalid_token(client: AsyncClient) -> None:
    resp = await client.get("/api/auth/verify?token=invalidtoken")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_verify_reuse_prevented(client: AsyncClient) -> None:
    """Verification token should be single-use."""
    settings = get_settings()
    await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    token = create_verification_token(settings.ALLOWED_EMAIL)
    await client.get(f"/api/auth/verify?token={token}")
    resp = await client.get(f"/api/auth/verify?token={token}")
    assert resp.status_code == 401


# --- Forgot / Reset Password ---


@pytest.mark.asyncio
@patch("app.routers.auth.enqueue_job", new_callable=AsyncMock)
async def test_register_enqueues_verification_email(
    mock_enqueue: AsyncMock,
    client: AsyncClient,
) -> None:
    mock_enqueue.return_value = "job-verify"
    settings = get_settings()
    resp = await client.post(
        "/api/auth/register",
        json={"email": settings.ALLOWED_EMAIL, "password": "securepass123"},
    )
    assert resp.status_code == 200
    mock_enqueue.assert_awaited_once()
    assert mock_enqueue.await_args.args[0] == "send_verification_email"
    assert mock_enqueue.await_args.args[1] == settings.ALLOWED_EMAIL


@pytest.mark.asyncio
@patch("app.routers.auth.enqueue_job", new_callable=AsyncMock)
async def test_forgot_password_enqueues_reset_email(
    mock_enqueue: AsyncMock,
    client: AsyncClient,
    admin_user: object,
) -> None:
    mock_enqueue.return_value = "job-reset"
    resp = await client.post(
        "/api/auth/forgot-password",
        json={"email": ADMIN_EMAIL},
    )
    assert resp.status_code == 200
    mock_enqueue.assert_awaited_once()
    assert mock_enqueue.await_args.args[0] == "send_reset_email"
    assert mock_enqueue.await_args.args[1] == ADMIN_EMAIL


@pytest.mark.asyncio
async def test_forgot_password_existing(
    client: AsyncClient, admin_user: object
) -> None:
    resp = await client.post(
        "/api/auth/forgot-password",
        json={"email": ADMIN_EMAIL},
    )
    assert resp.status_code == 200
    assert "reset link" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_forgot_password_nonexistent(client: AsyncClient) -> None:
    """Should return 200 even for unknown emails to prevent enumeration."""
    resp = await client.post(
        "/api/auth/forgot-password",
        json={"email": "nobody@example.com"},
    )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_reset_password_invalid_token(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/reset-password",
        json={"token": "badtoken", "new_password": "newstrong1pass"},
    )
    assert resp.status_code == 401
