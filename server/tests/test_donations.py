import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_donations_config_returns_structure(client: AsyncClient) -> None:
    resp = await client.get("/api/donations/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "stripe" in data
    assert "telegram" in data
    assert "crypto" in data
    assert isinstance(data["stripe"]["enabled"], bool)
    assert isinstance(data["telegram"]["enabled"], bool)


@pytest.mark.asyncio
async def test_donations_crypto_fields(client: AsyncClient) -> None:
    resp = await client.get("/api/donations/config")
    data = resp.json()
    crypto = data["crypto"]
    assert "btc" in crypto
    assert "eth" in crypto
