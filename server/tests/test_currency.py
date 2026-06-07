import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_expense_convert_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/expenses/convert",
        json={"amount": "10.00", "from_currency": "EUR", "to_currency": "PLN"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_expense_convert(auth_client: AsyncClient) -> None:
    resp = await auth_client.post(
        "/api/tools/expenses/convert",
        json={"amount": "100.00", "from_currency": "EUR", "to_currency": "USD"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["from_currency"] == "EUR"
    assert data["to_currency"] == "USD"
    assert float(data["converted"]) > 0
