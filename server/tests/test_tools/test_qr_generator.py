"""Tests for the public QR code generator."""

import pytest
from httpx import AsyncClient

_BASE = "/api/tools/qr-generator"


@pytest.mark.asyncio
async def test_qr_generator_create_and_svg(client: AsyncClient) -> None:
    resp = await client.post(_BASE, json={"content": "https://example.com"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["content_preview"] == "https://example.com"
    assert data["error_level"] == "M"
    assert data["svg_url"].endswith("/svg")

    svg_resp = await client.get(data["svg_url"])
    assert svg_resp.status_code == 200
    assert svg_resp.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in svg_resp.text
    assert "example.com" not in svg_resp.text


@pytest.mark.asyncio
async def test_qr_generator_list_includes_created(client: AsyncClient) -> None:
    create = await client.post(_BASE, json={"content": "hello-list", "label": "demo"})
    assert create.status_code == 201
    created_id = create.json()["id"]

    listed = await client.get(_BASE, params={"page": 1, "per_page": 20})
    assert listed.status_code == 200
    body = listed.json()
    ids = [item["id"] for item in body["items"]]
    assert created_id in ids


@pytest.mark.asyncio
async def test_qr_generator_rejects_empty_content(client: AsyncClient) -> None:
    resp = await client.post(_BASE, json={"content": "   "})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_qr_generator_not_found(client: AsyncClient) -> None:
    resp = await client.get(f"{_BASE}/999999")
    assert resp.status_code == 404
