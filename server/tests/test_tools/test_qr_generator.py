"""Tests for QR generator (public ephemeral + owner library)."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token
from tests.factories import create_user

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
    assert body["content"] == "https://saved.example"

    listed = await auth_client.get(_LIBRARY, params={"page": 1, "per_page": 20})
    assert listed.status_code == 200
    items = listed.json()["items"]
    ids = [item["id"] for item in items]
    assert qr_id in ids
    listed_item = next(item for item in items if item["id"] == qr_id)
    assert "content" not in listed_item
    assert listed_item["content_preview"] == "https://saved.example"

    svg_resp = await auth_client.get(body["svg_url"])
    assert svg_resp.status_code == 200
    assert svg_resp.headers["content-type"].startswith("image/svg+xml")
    assert "qr-" in svg_resp.headers.get("content-disposition", "")

    updated = await auth_client.patch(
        f"{_LIBRARY}/{qr_id}",
        json={"content": "https://updated.example", "label": "demo"},
    )
    assert updated.status_code == 200
    assert updated.json()["content_preview"] == "https://updated.example"
    assert updated.json()["label"] == "demo"
    assert updated.json()["svg"].startswith("<svg")


@pytest.mark.asyncio
async def test_qr_library_get_saved_includes_svg(auth_client: AsyncClient) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "get-one"})
    assert create.status_code == 201
    qr_id = create.json()["id"]
    got = await auth_client.get(f"{_LIBRARY}/{qr_id}")
    assert got.status_code == 200
    assert got.json()["content"] == "get-one"
    assert got.json()["svg"].startswith("<svg")


@pytest.mark.asyncio
async def test_qr_library_empty_patch_rejected(auth_client: AsyncClient) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "patch-me"})
    assert create.status_code == 201
    qr_id = create.json()["id"]
    resp = await auth_client.patch(f"{_LIBRARY}/{qr_id}", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_qr_library_delete(auth_client: AsyncClient) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "to-delete"})
    assert create.status_code == 201
    qr_id = create.json()["id"]
    deleted = await auth_client.delete(f"{_LIBRARY}/{qr_id}")
    assert deleted.status_code == 204
    missing = await auth_client.get(f"{_LIBRARY}/{qr_id}")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_qr_library_forbidden_for_other_user(
    client: AsyncClient,
    auth_client: AsyncClient,
    registry,
) -> None:
    create = await auth_client.post(_LIBRARY, json={"content": "secret-payload"})
    assert create.status_code == 201
    qr_id = create.json()["id"]
    svg_url = create.json()["svg_url"]

    other = await create_user(
        registry,
        email="other@glorng.dev",
        permissions=["qr-generator:read", "qr-generator:write"],
    )
    token = create_access_token(str(other.public_id), user_id=other.id)
    headers = {"Authorization": f"Bearer {token}"}

    assert (await client.get(svg_url, headers=headers)).status_code == 403
    assert (await client.get(f"{_LIBRARY}/{qr_id}", headers=headers)).status_code == 403
    assert (
        await client.patch(
            f"{_LIBRARY}/{qr_id}",
            json={"label": "hijack"},
            headers=headers,
        )
    ).status_code == 403
    assert (await client.delete(f"{_LIBRARY}/{qr_id}", headers=headers)).status_code == 403


@pytest.mark.asyncio
async def test_qr_library_list_scoped_to_owner(
    client: AsyncClient,
    auth_client: AsyncClient,
    registry,
) -> None:
    """List returns only the caller's codes (url-shortener owner scope)."""
    mine = await auth_client.post(_LIBRARY, json={"content": "owner-payload", "label": "mine"})
    assert mine.status_code == 201

    other = await create_user(
        registry,
        email="other-qr@glorng.dev",
        permissions=["qr-generator:read", "qr-generator:write"],
    )
    other_token = create_access_token(str(other.public_id), user_id=other.id)
    other_create = await client.post(
        _LIBRARY,
        json={"content": "other-payload", "label": "theirs"},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_create.status_code == 201

    listed = await client.get(
        _LIBRARY,
        params={"page": 1, "per_page": 20},
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert listed.status_code == 200
    items = listed.json()["items"]
    assert len(items) == 1
    assert items[0]["label"] == "theirs"
    assert items[0]["content_preview"] == "other-payload"
    assert "content" not in items[0]
