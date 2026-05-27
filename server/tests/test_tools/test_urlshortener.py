import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_short_url


@pytest.mark.asyncio
async def test_create_url_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com", "title": "Test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_url"] == "https://example.com/"
    assert data["title"] == "Test"
    assert "code" in data
    assert len(data["code"]) == 8


@pytest.mark.asyncio
async def test_list_urls_empty(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/url-shortener")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_urls_with_data(
    auth_client: AsyncClient, db: AsyncSession, admin_user: object
) -> None:
    await create_short_url(db, created_by=admin_user.id)  # type: ignore[union-attr]
    resp = await auth_client.get("/api/tools/url-shortener")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_delete_url(
    auth_client: AsyncClient, db: AsyncSession, admin_user: object
) -> None:
    url = await create_short_url(db, created_by=admin_user.id)  # type: ignore[union-attr]
    resp = await auth_client.delete(f"/api/tools/url-shortener/{url.id}")
    assert resp.status_code == 200
    assert "deleted" in resp.json()["message"].lower()


@pytest.mark.asyncio
async def test_delete_nonexistent_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.delete("/api/tools/url-shortener/99999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_redirect_short_url(
    client: AsyncClient, db: AsyncSession, admin_user: object
) -> None:
    url = await create_short_url(
        db,
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


@pytest.mark.asyncio
async def test_create_url_invalid_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "not-a-url"},
    )
    assert resp.status_code == 422
