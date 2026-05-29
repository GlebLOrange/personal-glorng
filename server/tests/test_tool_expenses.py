
from httpx import AsyncClient

EXPENSE_DATA = {
    "tool_name": "Cursor",
    "amount": "20.00",
    "currency": "USD",
    "expense_date": "2025-03-15",
    "category": "AI",
    "notes": "Pro subscription",
}


class TestToolExpensesCRUD:
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/tools/expenses")
        assert resp.status_code == 401

    async def test_create_expense(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tool_name"] == "Cursor"
        assert data["amount"] == "20.00"
        assert data["category"] == "AI"

    async def test_list_expenses(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        resp = await auth_client.get("/api/tools/expenses")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_get_expense(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        expense_id = create_resp.json()["id"]
        resp = await auth_client.get(f"/api/tools/expenses/{expense_id}")
        assert resp.status_code == 200
        assert resp.json()["tool_name"] == "Cursor"

    async def test_update_expense(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        expense_id = create_resp.json()["id"]
        resp = await auth_client.put(
            f"/api/tools/expenses/{expense_id}",
            json={"amount": "25.00", "notes": "Updated"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["amount"] == "25.00"
        assert data["notes"] == "Updated"

    async def test_delete_expense(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        expense_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/tools/expenses/{expense_id}")
        assert resp.status_code == 200

        get_resp = await auth_client.get(f"/api/tools/expenses/{expense_id}")
        assert get_resp.status_code == 404

    async def test_filter_by_tool_name(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "tool_name": "Vercel", "expense_date": "2025-04-01"},
        )
        resp = await auth_client.get("/api/tools/expenses?tool_name=cursor")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_filter_by_category(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "category": "Hosting", "tool_name": "Railway"},
        )
        resp = await auth_client.get("/api/tools/expenses?category=AI")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_list_categories(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        resp = await auth_client.get("/api/tools/expenses/categories")
        assert resp.status_code == 200
        assert "AI" in resp.json()

    async def test_summary_aggregation(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={
                **EXPENSE_DATA,
                "tool_name": "Cursor",
                "amount": "10.00",
                "expense_date": "2025-03-20",
            },
        )
        await auth_client.post(
            "/api/tools/expenses",
            json={
                **EXPENSE_DATA,
                "tool_name": "Vercel",
                "amount": "5.00",
                "category": "Hosting",
                "expense_date": "2025-04-10",
            },
        )
        resp = await auth_client.get("/api/tools/expenses/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == "35.00"
        assert len(data["by_month"]) == 2
        assert len(data["by_tool"]) == 2
        assert len(data["by_category"]) == 2

    async def test_filter_by_month(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "expense_date": "2025-06-01", "amount": "50.00"},
        )
        resp = await auth_client.get("/api/tools/expenses", params={"month": "2025-03"})
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_summary_month_param(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "expense_date": "2025-06-01", "amount": "50.00"},
        )
        resp = await auth_client.get(
            "/api/tools/expenses/summary",
            params={"month": "2025-06"},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == "50.00"

    async def test_summary_date_filter(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "expense_date": "2025-06-01", "amount": "50.00"},
        )
        resp = await auth_client.get(
            "/api/tools/expenses/summary",
            params={"date_from": "2025-06-01", "date_to": "2025-06-30"},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == "50.00"

    async def test_create_invalid_amount(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "amount": "0"},
        )
        assert resp.status_code == 422

    async def test_create_invalid_currency(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "currency": "GBP"},
        )
        assert resp.status_code == 422

    async def test_get_exchange_rates(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/tools/expenses/rates")
        assert resp.status_code == 200
        data = resp.json()
        assert data["base"] == "USD"
        assert set(data["rates"].keys()) == {"USD", "EUR", "PLN", "BYN"}

    async def test_summary_converts_to_display_currency(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/tools/expenses",
            json={**EXPENSE_DATA, "amount": "8.60", "currency": "EUR"},
        )
        resp = await auth_client.get(
            "/api/tools/expenses/summary",
            params={"display_currency": "USD"},
        )
        assert resp.status_code == 200
        assert resp.json()["total"] == "10.00"
        assert resp.json()["currency"] == "USD"
