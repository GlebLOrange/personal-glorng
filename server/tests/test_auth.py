from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from httpx import AsyncClient

import app.services.firebase_auth as firebase_auth_service
from app.core.deps import get_job_queue_dep
from app.core.security import (
    create_access_token,
    create_reset_token,
    create_verification_token,
    decode_token,
    require_matching_session_version,
)
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.main import app
from app.services.audit import AuditService
from app.services.auth import login_user
from app.services.user import get_user_by_email
from app.settings import get_settings
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
    assert resp.status_code == 201
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
    assert resp.status_code == 201

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
    assert resp.json()["message"] == "Login successful"
    assert resp.cookies.get("access_token")
    assert resp.cookies.get("refresh_token")


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


# --- Firebase Google Login ---


def _mock_firebase_token(
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
) -> None:
    settings = get_settings()
    settings.FIREBASE_AUTH_ENABLED = True
    settings.FIREBASE_PROJECT_ID = "test-firebase-project"
    monkeypatch.setattr(
        firebase_auth_service, "_firebase_app", lambda _settings: object()
    )
    def _verify_id_token(_token: str, **_kwargs: object) -> dict[str, object]:
        return payload

    monkeypatch.setattr(
        firebase_auth_service.firebase_auth,
        "verify_id_token",
        _verify_id_token,
    )


@pytest.mark.asyncio
async def test_firebase_login_creates_restricted_user_and_enqueues_reset(
    client: AsyncClient,
    registry: DatabaseRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _mock_firebase_token(
        monkeypatch,
        {
            "email": "Google.User@Glorng.dev",
            "email_verified": True,
            "name": "Google User",
            "firebase": {"sign_in_provider": "google.com"},
        },
    )
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-reset")
    app.dependency_overrides[get_job_queue_dep] = lambda: mock_queue
    try:
        resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    finally:
        app.dependency_overrides.pop(get_job_queue_dep, None)

    assert resp.status_code == 200
    assert resp.cookies.get("access_token")
    assert resp.cookies.get("refresh_token")
    user = await get_user_by_email(registry, "google.user@glorng.dev")
    assert user is not None
    assert user.is_verified is True
    assert user.permissions == []
    assert user.display_name == "Google User"
    mock_queue.enqueue.assert_awaited_once()
    assert mock_queue.enqueue.await_args.args[0] == JobName.SEND_RESET_EMAIL
    assert mock_queue.enqueue.await_args.args[1] == "google.user@glorng.dev"


@pytest.mark.asyncio
async def test_firebase_login_existing_user_does_not_grant_permissions_or_email(
    client: AsyncClient,
    registry: DatabaseRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    existing = await firebase_auth_service.create_user(
        registry,
        email="existing@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
        is_verified=True,
    )
    _mock_firebase_token(
        monkeypatch,
        {
            "email": "existing@glorng.dev",
            "email_verified": True,
            "name": "Existing",
            "firebase": {"sign_in_provider": "google.com"},
        },
    )
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-reset")
    app.dependency_overrides[get_job_queue_dep] = lambda: mock_queue
    try:
        resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    finally:
        app.dependency_overrides.pop(get_job_queue_dep, None)

    assert resp.status_code == 200
    user = await get_user_by_email(registry, "existing@glorng.dev")
    assert user is not None
    assert user.id == existing.id
    assert user.permissions == []
    mock_queue.enqueue.assert_not_awaited()


@pytest.mark.asyncio

@pytest.mark.asyncio
async def test_firebase_login_rejects_unverified_password_account(
    client: AsyncClient,
    registry: DatabaseRegistry,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await firebase_auth_service.create_user(
        registry,
        email="preaccount@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
        is_verified=False,
    )
    _mock_firebase_token(
        monkeypatch,
        {
            "email": "preaccount@glorng.dev",
            "email_verified": True,
            "name": "Victim",
            "firebase": {"sign_in_provider": "google.com"},
        },
    )
    resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    assert resp.status_code == 409
    user = await get_user_by_email(registry, "preaccount@glorng.dev")
    assert user is not None
    assert user.is_verified is False


async def test_firebase_login_rejects_when_disabled(client: AsyncClient) -> None:
    settings = get_settings()
    settings.FIREBASE_AUTH_ENABLED = False
    settings.FIREBASE_PROJECT_ID = "test-firebase-project"

    resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_firebase_login_rejects_missing_project(client: AsyncClient) -> None:
    settings = get_settings()
    settings.FIREBASE_AUTH_ENABLED = True
    settings.FIREBASE_PROJECT_ID = ""

    resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_firebase_login_rejects_invalid_token(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = get_settings()
    settings.FIREBASE_AUTH_ENABLED = True
    settings.FIREBASE_PROJECT_ID = "test-firebase-project"
    monkeypatch.setattr(
        firebase_auth_service, "_firebase_app", lambda _settings: object()
    )

    def _raise_invalid(_token: str, _app: object) -> dict[str, object]:
        raise ValueError("bad token")

    monkeypatch.setattr(
        firebase_auth_service.firebase_auth,
        "verify_id_token",
        _raise_invalid,
    )

    resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
    assert resp.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        {
            "email": "unverified@glorng.dev",
            "email_verified": False,
            "firebase": {"sign_in_provider": "google.com"},
        },
        {
            "email": "password@glorng.dev",
            "email_verified": True,
            "firebase": {"sign_in_provider": "password"},
        },
    ],
)
async def test_firebase_login_rejects_unverified_or_non_google_token(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    payload: dict[str, object],
) -> None:
    _mock_firebase_token(monkeypatch, payload)

    resp = await client.post("/api/auth/firebase", json={"id_token": "x" * 24})
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
    resp = await client.post("/api/auth/verify", json={"token": token})
    assert resp.status_code == 200
    assert "verified" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_verify_invalid_token(client: AsyncClient) -> None:
    resp = await client.post("/api/auth/verify", json={"token": "invalidtoken"})
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
    await client.post("/api/auth/verify", json={"token": token})
    resp = await client.post("/api/auth/verify", json={"token": token})
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
        assert resp.status_code == 201
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
    assert login.cookies.get("access_token")


@pytest.mark.asyncio
async def test_reset_password_revokes_prior_sessions(
    client: AsyncClient,
    db,
) -> None:
    from tests.factories import create_user

    user = await create_user(
        db,
        email="reset-revoke@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200
    old_access = login.cookies["access_token"]
    old_refresh = login.cookies["refresh_token"]

    new_password = "ResetTestPass456!"
    reset = await client.post(
        "/api/auth/reset-password",
        json={
            "token": create_reset_token(user.email),
            "new_password": new_password,
            "password_confirm": new_password,
        },
    )
    assert reset.status_code == 200

    me = await client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {old_access}"},
    )
    assert me.status_code == 401

    refresh = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": old_refresh},
    )
    assert refresh.status_code == 401


def test_access_token_includes_session_version() -> None:
    token = create_access_token("subject", user_id=1, session_version=3)
    payload = decode_token(token)
    assert payload["sv"] == 3
    assert payload["uid"] == 1


def test_require_matching_session_version_fail_closed() -> None:
    with pytest.raises(ValueError, match="missing session version"):
        require_matching_session_version({"type": "access"}, 0)

    require_matching_session_version({"sv": 2}, 2)

    with pytest.raises(ValueError, match="revoked"):
        require_matching_session_version({"sv": 1}, 2)


def test_legacy_access_token_without_sv_is_rejected_by_matcher() -> None:
    """Tokens minted before session_version must not validate (D1 fail closed)."""
    settings = get_settings()
    legacy = jwt.encode(
        {
            "sub": "subject",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "iat": datetime.now(UTC),
            "type": "access",
            "jti": "legacy-jti",
        },
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    payload = decode_token(legacy)
    with pytest.raises(ValueError, match="missing session version"):
        require_matching_session_version(payload, 0)


@pytest.mark.asyncio
async def test_login_user_dual_writes_audit_to_postgres(
    registry: DatabaseRegistry,
    admin_user: User,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    await registry.users.update_fields(admin_user.id, is_verified=True)  # type: ignore[union-attr]

    record_postgres = AsyncMock()
    monkeypatch.setattr(AuditService, "_record_postgres", record_postgres)
    mock_settings = MagicMock()
    mock_settings.enable_postgres.return_value = True
    monkeypatch.setattr("app.services.audit.get_settings", lambda: mock_settings)

    audit = AuditService(registry, postgres_db=AsyncMock())
    await login_user(registry, audit, ADMIN_EMAIL, ADMIN_PASSWORD)

    record_postgres.assert_called_once()
