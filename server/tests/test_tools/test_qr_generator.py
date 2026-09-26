"""Tests for the ephemeral QR code generator."""

import pytest
from httpx import AsyncClient

_BASE = "/api/tools/qr-generator"


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
async def test_qr_generator_list_removed(client: AsyncClient) -> None:
    resp = await client.get(_BASE)
    assert resp.status_code == 405


@pytest.mark.asyncio
async def test_qr_generator_svg_route_removed(client: AsyncClient) -> None:
    resp = await client.get(f"{_BASE}/1/svg")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_qr_generator_rejects_empty_content(client: AsyncClient) -> None:
    resp = await client.post(_BASE, json={"content": "   "})
    assert resp.status_code == 422
