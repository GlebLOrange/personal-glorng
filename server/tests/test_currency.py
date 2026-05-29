import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_currency_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/currency/convert",
        json={"amount": "10.00", "from_currency": "EUR", "to_currency": "PLN"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_currency_convert(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/currency/convert",
        json={"amount": "100.00", "from_currency": "EUR", "to_currency": "USD"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["from_currency"] == "EUR"
    assert data["to_currency"] == "USD"
    assert float(data["converted"]) > 0


@pytest.mark.asyncio
async def test_currency_rates(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/currency/rates")
    assert resp.status_code == 200
    assert set(resp.json()["rates"].keys()) == {"USD", "EUR", "PLN", "BYN"}
