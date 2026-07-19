import pytest
from httpx import AsyncClient

from app.services.user import default_owner_permissions
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
    token = login.cookies["access_token"]

    resp = await client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_users_search_escapes_regex_metacharacters(
    auth_client: AsyncClient,
    db,
) -> None:
    await create_user(
        db,
        email="literal.plus+user@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )
    await create_user(
        db,
        email="regex-bait@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=[],
    )

    resp = await auth_client.get(
        "/api/admin/users",
        params={"search": "literal.plus+user"},
    )
    assert resp.status_code == 200
    emails = {row["email"] for row in resp.json()["items"]}
    assert "literal.plus+user@glorng.dev" in emails
    assert "regex-bait@glorng.dev" not in emails

    meta_resp = await auth_client.get(
        "/api/admin/users",
        params={"search": ".*"},
    )
    assert meta_resp.status_code == 200
    meta_emails = {row["email"] for row in meta_resp.json()["items"]}
    assert "regex-bait@glorng.dev" not in meta_emails


@pytest.mark.asyncio
async def test_admin_users_stats(auth_client: AsyncClient, admin_user: object) -> None:
    resp = await auth_client.get("/api/admin/users/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert data["superuser_count"] >= 1


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
async def test_cannot_remove_last_superuser(client: AsyncClient, db) -> None:
    user = await create_user(
        db,
        email="lone-super@glorng.dev",
        password=STRONG_PASSWORD,
        permissions=default_owner_permissions(),
        is_protected=False,
    )
    login = await client.post(
        "/api/auth/login",
        json={"email": user.email, "password": STRONG_PASSWORD},
    )
    token = login.cookies["access_token"]

    resp = await client.patch(
        f"/api/admin/users/{user.public_id}/permissions",
        headers={"Authorization": f"Bearer {token}"},
        json={"permissions": ["expenses:read"]},
    )
    assert resp.status_code == 409
    assert "last admin" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cannot_update_protected_user_permissions(
    auth_client: AsyncClient,
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

    resp = await auth_client.patch(
        f"/api/admin/users/{admin_user.public_id}/permissions",
        json={"permissions": ["expenses:read"]},
    )
    assert resp.status_code == 409
    assert "protected" in resp.json()["detail"].lower()
