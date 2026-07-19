from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.core.deps import get_job_queue_dep
from app.main import app
from app.services.user import default_owner_permissions
from tests.conftest import ADMIN_EMAIL, ADMIN_PASSWORD, STRONG_PASSWORD
from tests.factories import create_user


@pytest.mark.asyncio
async def test_update_profile(auth_client: AsyncClient) -> None:
    resp = await auth_client.patch(
        "/api/auth/me",
        json={"display_name": "Admin User", "timezone": "Europe/Warsaw"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Admin User"
    assert data["timezone"] == "Europe/Warsaw"


@pytest.mark.asyncio
async def test_change_password(auth_client: AsyncClient, client: AsyncClient) -> None:
    new_password = "NewStrongPass1!"
    resp = await auth_client.post(
        "/api/auth/change-password",
        json={
            "current_password": ADMIN_PASSWORD,
            "new_password": new_password,
            "password_confirm": new_password,
        },
    )
    assert resp.status_code == 200

    login = await client.post(
        "/api/auth/login",
        json={"email": "admin@admin.admin", "password": new_password},
    )
    assert login.status_code == 200


@pytest.mark.asyncio
async def test_change_password_revokes_old_token(
    client: AsyncClient,
    db,
) -> None:
    user = await create_user(
        db,
        email="revoke-me@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200
    old_token = login.cookies["access_token"]
    headers = {"Authorization": f"Bearer {old_token}"}

    new_password = "NewStrongPass1!"
    change = await client.post(
        "/api/auth/change-password",
        headers=headers,
        json={
            "current_password": STRONG_PASSWORD,
            "new_password": new_password,
            "password_confirm": new_password,
        },
    )
    assert change.status_code == 200

    me = await client.get("/api/auth/me", headers=headers)
    assert me.status_code == 401


@pytest.mark.asyncio
async def test_change_password_wrong_current(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/auth/change-password",
        json={
            "current_password": "WrongPass123!",
            "new_password": "AnotherPass123!",
            "password_confirm": "AnotherPass123!",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_change_email_requires_reverify(
    auth_client: AsyncClient,
) -> None:
    mock_queue = AsyncMock()
    mock_queue.enqueue = AsyncMock(return_value="job-verify")
    app.dependency_overrides[get_job_queue_dep] = lambda: mock_queue
    try:
        resp = await auth_client.patch(
            "/api/auth/me/email",
            json={
                "email": "renamed@glorng.dev",
                "current_password": ADMIN_PASSWORD,
            },
        )
        assert resp.status_code == 200
        mock_queue.enqueue.assert_awaited_once()
    finally:
        app.dependency_overrides.pop(get_job_queue_dep, None)

    # Email change bumps session_version and clears cookies → prior session is dead.
    me = await auth_client.get("/api/auth/me")
    assert me.status_code == 401


@pytest.mark.asyncio
async def test_change_password_revokes_other_device_refresh(
    client: AsyncClient,
    db,
) -> None:
    """Password change must invalidate refresh tokens not presented in the request."""
    user = await create_user(
        db,
        email="other-device@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    device_a = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert device_a.status_code == 200
    device_b = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert device_b.status_code == 200
    other_refresh = device_b.cookies["refresh_token"]

    new_password = "NewStrongPass1!"
    change = await client.post(
        "/api/auth/change-password",
        headers={"Authorization": f"Bearer {device_a.cookies['access_token']}"},
        json={
            "current_password": STRONG_PASSWORD,
            "new_password": new_password,
            "password_confirm": new_password,
        },
    )
    assert change.status_code == 200

    reuse = await client.post(
        "/api/auth/refresh",
        json={"refresh_token": other_refresh},
    )
    assert reuse.status_code == 401


@pytest.mark.asyncio
async def test_preferences_round_trip(auth_client: AsyncClient) -> None:
    patch_resp = await auth_client.patch(
        "/api/auth/me/preferences",
        json={"display_currency": "EUR"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["display_currency"] == "EUR"

    get_resp = await auth_client.get("/api/auth/me/preferences")
    assert get_resp.status_code == 200
    assert get_resp.json()["display_currency"] == "EUR"


@pytest.mark.asyncio
async def test_delete_regular_user(client: AsyncClient, db) -> None:
    user = await create_user(
        db,
        email="delete-me@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200
    token = login.cookies["access_token"]

    delete = await client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": STRONG_PASSWORD, "confirm": True},
    )
    assert delete.status_code == 200

    me = await client.get("/api/auth/me")
    assert me.status_code == 401


@pytest.mark.asyncio
async def test_cannot_delete_protected_account(
    client: AsyncClient,
    admin_user: object,
    db,
) -> None:
    await create_user(
        db,
        email="other-super@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=default_owner_permissions(),
        is_protected=False,
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert login.status_code == 200
    token = login.cookies["access_token"]

    delete = await client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": ADMIN_PASSWORD, "confirm": True},
    )
    assert delete.status_code == 409
    assert "protected" in delete.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cannot_delete_last_superuser(client: AsyncClient, db) -> None:
    user = await create_user(
        db,
        email="last-super@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=default_owner_permissions(),
        is_protected=False,
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    assert login.status_code == 200
    token = login.cookies["access_token"]

    delete = await client.request(
        "DELETE",
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"current_password": STRONG_PASSWORD, "confirm": True},
    )
    assert delete.status_code == 409
    assert "last superuser" in delete.json()["detail"].lower()
