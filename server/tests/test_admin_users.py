import pytest
from httpx import AsyncClient

from tests.conftest import STRONG_PASSWORD
from tests.factories import create_user


@pytest.mark.asyncio
async def test_list_users_requires_superuser(client: AsyncClient, db) -> None:
    user = await create_user(
        db,
        email="regular@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    token = login.json()["access_token"]

    resp = await client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_users_as_superuser(auth_client: AsyncClient, admin_user: object) -> None:
    resp = await auth_client.get("/api/admin/users")
    assert resp.status_code == 200
    emails = {row["email"] for row in resp.json()}
    assert "admin@glorng.dev" in emails


@pytest.mark.asyncio
async def test_update_user_permissions(auth_client: AsyncClient, db) -> None:
    user = await create_user(
        db,
        email="grantee@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )

    resp = await auth_client.patch(
        f"/api/admin/users/{user.public_id}/permissions",
        json={"permissions": ["expenses:read", "expenses:write"]},
    )
    assert resp.status_code == 200
    assert set(resp.json()["permissions"]) == {"expenses:read", "expenses:write"}


@pytest.mark.asyncio
async def test_cannot_remove_last_superuser(auth_client: AsyncClient, admin_user: object) -> None:
    resp = await auth_client.patch(
        f"/api/admin/users/{admin_user.public_id}/permissions",
        json={"permissions": ["expenses:read"]},
    )
    assert resp.status_code == 409
