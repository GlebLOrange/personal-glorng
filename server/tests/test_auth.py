from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.deps import get_job_queue_dep
from app.core.security import create_reset_token, create_verification_token
from app.db.registry import DatabaseRegistry
from app.main import app
from app.services.user import get_user_by_email
from app.workers.job_names import JobName
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, STRONG_PASSWORD

# --- Registration ---


@pytest.mark.asyncio
async def test_register_open_email(
    client: AsyncClient, registry: DatabaseRegistry
) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "new.user@glorng.dev",
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    assert resp.status_code == 200
    assert "Registration successful" in resp.json()["message"]

    user = await get_user_by_email(registry, "new.user@glorng.dev")
    assert user is not None
    assert user.permissions == []
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_register_normalizes_email(
    client: AsyncClient, registry: DatabaseRegistry
) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "  MixedCase@Glorng.dev ",
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    assert resp.status_code == 200

    user = await get_user_by_email(registry, "mixedcase@glorng.dev")
    assert user is not None


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient, admin_user: object) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": ADMIN_EMAIL,
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "weak@glorng.dev",
            "password": "short",
            "password_confirm": "short",
            "accept_terms": True,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_common_password(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "common@glorng.dev",
            "password": "MyCommonPass1!",
            "password_confirm": "MyCommonPass1!",
            "accept_terms": True,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_requires_terms(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/register",
        json={
            "email": "terms@glorng.dev",
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": False,
        },
    )
    assert resp.status_code == 422


# --- Login ---


@pytest.mark.asyncio
async def test_login_unverified(client: AsyncClient) -> None:
    await client.post(
        "/api/auth/register",
        json={
            "email": "unverified@glorng.dev",
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    resp = await client.post(
        "/api/auth/login",
        json={"email": "unverified@glorng.dev", "password": STRONG_PASSWORD},
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
        json={"email": ADMIN_EMAIL, "password": "WrongPass123!"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/auth/login",
        json={"email": "nobody@glorng.dev", "password": STRONG_PASSWORD},
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
    assert "platform:superuser" in data["permissions"]
    assert data["is_verified"] is True
    assert "timezone" in data
    assert "preferences" in data


# --- Token Refresh ---


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, login_tokens: dict[str, str]) -> None:
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
    email = "verify-me@glorng.dev"
    await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    token = create_verification_token(email)
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
    email = "verify-once@glorng.dev"
    await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
            "accept_terms": True,
        },
    )
    token = create_verification_token(email)
    await client.get(f"/api/auth/verify?token={token}")
    resp = await client.get(f"/api/auth/verify?token={token}")
    assert resp.status_code == 401


# --- Forgot / Reset Password ---


@pytest.mark.asyncio
async def test_register_enqueues_verification_email(
    client: AsyncClient,
) -> None:
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-verify")
    app.dependency_overrides[get_job_queue_dep] = lambda: mock_queue
    email = "enqueue@glorng.dev"
    try:
        resp = await client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": STRONG_PASSWORD,
                "password_confirm": STRONG_PASSWORD,
                "accept_terms": True,
            },
        )
        assert resp.status_code == 200
        mock_queue.enqueue.assert_awaited_once()
        assert mock_queue.enqueue.await_args.args[0] == JobName.SEND_VERIFICATION_EMAIL
        assert mock_queue.enqueue.await_args.args[1] == email
    finally:
        app.dependency_overrides.pop(get_job_queue_dep, None)


@pytest.mark.asyncio
async def test_forgot_password_enqueues_reset_email(
    client: AsyncClient,
    admin_user: object,
) -> None:
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-reset")
    app.dependency_overrides[get_job_queue_dep] = lambda: mock_queue
    try:
        resp = await client.post(
            "/api/auth/forgot-password",
            json={"email": ADMIN_EMAIL},
        )
        assert resp.status_code == 200
        mock_queue.enqueue.assert_awaited_once()
        assert mock_queue.enqueue.await_args.args[0] == JobName.SEND_RESET_EMAIL
        assert mock_queue.enqueue.await_args.args[1] == ADMIN_EMAIL
    finally:
        app.dependency_overrides.pop(get_job_queue_dep, None)


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
        json={
            "token": "badtoken",
            "new_password": STRONG_PASSWORD,
            "password_confirm": STRONG_PASSWORD,
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_reset_password_success(
    client: AsyncClient,
    admin_user: object,
) -> None:
    new_password = "ResetTestPass456!"
    token = create_reset_token(ADMIN_EMAIL)
    resp = await client.post(
        "/api/auth/reset-password",
        json={
            "token": token,
            "new_password": new_password,
            "password_confirm": new_password,
        },
    )
    assert resp.status_code == 200
    assert "success" in resp.json()["message"].lower()

    login = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": new_password},
    )
    assert login.status_code == 200
    assert "access_token" in login.json()
