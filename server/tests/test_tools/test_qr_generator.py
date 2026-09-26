"""Tests for QR generator (public ephemeral + admin library)."""

import pytest
from httpx import AsyncClient

_BASE = "/api/tools/qr-generator"
_LIBRARY = f"{_BASE}/library"


@pytest.mark.asyncio
async def test_qr_generator_returns_inline_svg(client: AsyncClient) -> None:
    resp = await client.post(_BASE, json={"content": "https://example.com"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["content_preview"] == "https://example.com"
    assert data["error_level"] == "M"
    assert data["svg"].startswith("<svg")
    assert "example.com" not in data["svg"]


@pytest.mark.asyncio
async def test_qr_generator_rejects_empty_content(client: AsyncClient) -> None:
    resp = await client.post(_BASE, json={"content": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_qr_library_requires_auth(client: AsyncClient) -> None:
    resp = await client.get(_LIBRARY)
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_qr_library_create_update_and_svg(auth_client: AsyncClient) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "https://saved.example"})
    assert create.status_code == 201
    body = create.json()
    qr_id = body["id"]
    assert body["svg"].startswith("<svg")
    assert body["svg_url"].endswith("/svg")

    listed = await auth_client.get(_LIBRARY, params={"page": 1, "per_page": 20})
    assert listed.status_code == 200
    ids = [item["id"] for item in listed.json()["items"]]
    assert qr_id in ids

    svg_resp = await auth_client.get(body["svg_url"])
    assert svg_resp.status_code == 200
    assert svg_resp.headers["content-type"].startswith("image/svg+xml")

    updated = await auth_client.patch(
        f"{_LIBRARY}/{qr_id}",
        json={"content": "https://updated.example", "label": "demo"},
    )
    assert updated.status_code == 200
    assert updated.json()["content_preview"] == "https://updated.example"
    assert updated.json()["label"] == "demo"
    assert updated.json()["svg"].startswith("<svg")


@pytest.mark.asyncio
async def test_qr_library_get_saved(auth_client: AsyncClient) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "get-one"})
    assert create.status_code == 201
    qr_id = create.json()["id"]
    got = await auth_client.get(f"{_LIBRARY}/{qr_id}")
    assert got.status_code == 200
    assert got.json()["content"] == "get-one"


@pytest.mark.asyncio
async def test_qr_library_svg_forbidden_for_other_user(
    client: AsyncClient,
    auth_client: AsyncClient,
    registry,
) -> None:
    from tests.factories import create_user

    create = await auth_client.post(_LIBRARY, json={"content": "secret-payload"})
    assert create.status_code == 201
    svg_url = create.json()["svg_url"]

    other = await create_user(
        registry,
        email="other@glorng.dev",
        permissions=["qr-generator:read"],
    )
    from app.core.security import create_access_token

    token = create_access_token(str(other.public_id), user_id=other.id)
    client.headers["Authorization"] = f"Bearer {token}"
    try:
        resp = await client.get(svg_url)
        assert resp.status_code == 403
    finally:
        client.headers.pop("Authorization", None)
