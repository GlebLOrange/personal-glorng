import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_short_url


@pytest.mark.asyncio
async def test_create_short_url(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com", "title": "Example"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["original_url"] == "https://example.com/"
    assert data["title"] == "Example"
    assert "code" in data
    assert len(data["code"]) == 8


@pytest.mark.asyncio
async def test_create_short_url_unauthorized(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_list_urls(auth_client: AsyncClient) -> None:
    await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    resp = await auth_client.get("/api/tools/url-shortener")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_redirect_short_url(
    client: AsyncClient,
    db: AsyncSession,
    admin_user,  # noqa: ANN001
) -> None:
    url = await create_short_url(db, created_by=admin_user.id)
    resp = await client.get(f"/s/{url.code}", follow_redirects=False)
    assert resp.status_code == 307
    assert resp.headers["location"] == "https://example.com"


@pytest.mark.asyncio
async def test_redirect_not_found(client: AsyncClient) -> None:
    resp = await client.get("/s/nonexist", follow_redirects=False)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_url(auth_client: AsyncClient) -> None:
    create_resp = await auth_client.post(
        "/api/tools/url-shortener",
        json={"original_url": "https://example.com"},
    )
    url_id = create_resp.json()["id"]
    resp = await auth_client.delete(f"/api/tools/url-shortener/{url_id}")
    assert resp.status_code == 200
