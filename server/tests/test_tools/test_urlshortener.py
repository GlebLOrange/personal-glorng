import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from app.db.registry import DatabaseRegistry
from tests.factories import create_short_url, create_user


@pytest.mark.asyncio
async def test_create_url_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_url"] == "https://example.com/"
    assert "code" in data
    assert len(data["code"]) == 8


@pytest.mark.asyncio
async def test_create_url_blocks_private_host(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/url-shortener",
        json={"original_url": "http://127.0.0.1/internal"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_create_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com", "title": "Example"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_url"] == "https://example.com/"
    assert data["title"] == "Example"
    assert "code" in data
    assert len(data["code"]) == 8


@pytest.mark.asyncio
async def test_create_url_invalid_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "not-a-url"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_urls_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/url-shortener")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_urls_empty(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/url-shortener")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["per_page"] == 9


@pytest.mark.asyncio
async def test_list_urls_scoped_to_owner(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    other_user = await create_user(
        registry,
        email="other@glorng.dev",
        permissions=["url-shortener:read", "url-shortener:write"],
    )
    await create_short_url(registry, created_by=admin_user.id, title="Admin link")  # type: ignore[union-attr]
    await create_short_url(registry, created_by=other_user.id, title="Other link")

    other_token = create_access_token(str(other_user.public_id), user_id=other_user.id)
    resp = await client.get(
        "/api/tools/url-shortener",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["title"] == "Other link"


@pytest.mark.asyncio
async def test_update_url_title(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com", "title": "Before"},
    )
    url_id = create_resp.json()["id"]
    resp = await auth_client.patch(
        f"/api/tools/url-shortener/{url_id}",
        json={"title": "After"},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "After"


@pytest.mark.asyncio
async def test_update_url_clear_title(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com", "title": "To clear"},
    )
    url_id = create_resp.json()["id"]
    resp = await auth_client.patch(
        f"/api/tools/url-shortener/{url_id}",
        json={"title": None},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] is None


@pytest.mark.asyncio
async def test_update_other_users_url_forbidden(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    url = await create_short_url(registry, created_by=admin_user.id, title="Admin link")  # type: ignore[union-attr]
    other_user = await create_user(
        registry,
        email="updater@glorng.dev",
        permissions=["url-shortener:read", "url-shortener:write"],
    )
    other_token = create_access_token(str(other_user.public_id), user_id=other_user.id)
    resp = await client.patch(
        f"/api/tools/url-shortener/{url.id}",
        json={"title": "Hijacked"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_update_nonexistent_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.patch(
        "/api/tools/url-shortener/99999",
        json={"title": "Nope"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_url_via_api(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    url_id = create_resp.json()["id"]
    resp = await auth_client.delete(f"/api/tools/url-shortener/{url_id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_url(
    auth_client: AsyncClient, registry: DatabaseRegistry, admin_user: object
) -> None:
    url = await create_short_url(registry, created_by=admin_user.id)  # type: ignore[union-attr]
    resp = await auth_client.delete(f"/api/tools/url-shortener/{url.id}")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_other_users_url_forbidden(
    client: AsyncClient,
    registry: DatabaseRegistry,
    admin_user: object,
) -> None:
    url = await create_short_url(registry, created_by=admin_user.id)  # type: ignore[union-attr]
    other_user = await create_user(
        registry,
        email="deleter@glorng.dev",
        permissions=["url-shortener:read", "url-shortener:write"],
    )
    other_token = create_access_token(str(other_user.public_id), user_id=other_user.id)
    resp = await client.delete(
        f"/api/tools/url-shortener/{url.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_nonexistent_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.delete("/api/tools/url-shortener/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_redirect_short_url(
    client: AsyncClient, registry: DatabaseRegistry, admin_user: object
) -> None:
    url = await create_short_url(
        registry,
        original_url="https://example.com",
        created_by=admin_user.id,  # type: ignore[union-attr]
    )
    resp = await client.get(f"/s/{url.code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_nonexistent_code(client: AsyncClient) -> None:
    resp = await client.get("/s/nonexist", follow_redirects=False)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_redirect_invalid_code_chars(client: AsyncClient) -> None:
    resp = await client.get("/s/bad!@#code", follow_redirects=False)
    assert resp.status_code == 422
