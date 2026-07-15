"""Tests for the public expense calculator endpoints."""

import pytest
from httpx import AsyncClient

from tests.factories import create_user

STATE_PAYLOAD = {
    "display_currency": "PLN",
    "line_items": [{"label": "Coffee", "amount": "12.50", "currency": "PLN"}],
    "budget_rows": [{"name": "Food", "budget": "500.00", "spent": "120.00"}],
}


@pytest.mark.asyncio
async def test_rates_unauthenticated(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/expense-calculator/rates")
    assert resp.status_code == 200
    data = resp.json()
    assert "rates" in data
    assert "base" in data


@pytest.mark.asyncio
async def test_convert_unauthenticated(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/expense-calculator/convert",
        json={"amount": "100.00", "from_currency": "EUR", "to_currency": "PLN"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["from_currency"] == "EUR"
    assert data["to_currency"] == "PLN"
    assert float(data["converted"]) > 0


@pytest.mark.asyncio
async def test_convert_invalid_amount(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/tools/expense-calculator/convert",
        json={"amount": "0", "from_currency": "EUR", "to_currency": "PLN"},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_state_requires_auth(client: AsyncClient) -> None:
    resp = await client.get("/api/tools/expense-calculator/state")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_state_requires_superuser(client: AsyncClient, registry) -> None:
    user = await create_user(
        registry,
        email="reader@glorng.dev",
        permissions=["expenses:read"],
    )
    from app.core.security import create_access_token

    token = create_access_token(str(user.public_id), user_id=user.id)
    client.headers["Authorization"] = f"Bearer {token}"
    resp = await client.get("/api/tools/expense-calculator/state")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_state_round_trip(auth_client: AsyncClient) -> None:
    put_resp = await auth_client.put(
        "/api/tools/expense-calculator/state",
        json=STATE_PAYLOAD,
    )
    assert put_resp.status_code == 200
    data = put_resp.json()
    assert data["display_currency"] == "PLN"
    assert len(data["line_items"]) == 1
    assert data["saved_at"] is not None

    get_resp = await auth_client.get("/api/tools/expense-calculator/state")
    assert get_resp.status_code == 200
    assert get_resp.json()["line_items"][0]["label"] == "Coffee"


@pytest.mark.asyncio
async def test_state_caps_line_items(auth_client: AsyncClient) -> None:
    items = [{"label": f"Item {i}", "amount": "1.00"} for i in range(51)]
    resp = await auth_client.put(
        "/api/tools/expense-calculator/state",
        json={"display_currency": "PLN", "line_items": items, "budget_rows": []},
    )
    assert resp.status_code == 422
