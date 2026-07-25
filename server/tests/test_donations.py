import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_donations_config_returns_structure(client: AsyncClient) -> None:
    resp = await client.get("/api/donations/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "stripe" in data
    assert "paypal" in data
    assert "patreon" in data
    assert isinstance(data["stripe"]["enabled"], bool)
    assert isinstance(data["stripe"]["checkout_enabled"], bool)
    assert isinstance(data["paypal"]["enabled"], bool)
    assert isinstance(data["patreon"]["enabled"], bool)


@pytest.mark.asyncio
async def test_donations_stripe_fields(client: AsyncClient) -> None:
    resp = await client.get("/api/donations/config")
    data = resp.json()
    stripe = data["stripe"]
    assert "url" in stripe
    assert "checkout_enabled" in stripe
