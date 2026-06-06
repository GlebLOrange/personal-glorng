from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.tool_expense_category import ToolExpenseCategoryService

EXPENSE_DATA = {
    "tool_name": "Milk",
    "amount": "5.00",
    "currency": "PLN",
    "expense_date": "2025-03-15",
    "category": "Groceries",
    "notes": None,
}


class TestExpenseCategories:
    async def test_list_default_categories(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/tools/expenses/categories")
        assert resp.status_code == 200
        names = [item["name"] for item in resp.json()]
        assert "Groceries" in names
        assert "Home" in names
        assert "Transport" in names

    async def test_create_and_rename_category(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/tools/expenses/categories",
            json={"name": "Pets"},
        )
        assert create_resp.status_code == 200
        category_id = create_resp.json()["id"]

        rename_resp = await auth_client.put(
            f"/api/tools/expenses/categories/{category_id}",
            json={"name": "Pet supplies"},
        )
        assert rename_resp.status_code == 200
        assert rename_resp.json()["name"] == "Pet supplies"

    async def test_delete_unused_category(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/tools/expenses/categories",
            json={"name": "Temp"},
        )
        category_id = create_resp.json()["id"]
        delete_resp = await auth_client.delete(
            f"/api/tools/expenses/categories/{category_id}",
        )
        assert delete_resp.status_code == 200

    async def test_cannot_delete_category_in_use(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        groceries = next(
            item for item in categories.json() if item["name"] == "Groceries"
        )
        delete_resp = await auth_client.delete(
            f"/api/tools/expenses/categories/{groceries['id']}",
        )
        assert delete_resp.status_code == 422

    async def test_update_category_budget(self, auth_client: AsyncClient):
        categories = await auth_client.get("/api/tools/expenses/categories")
        groceries = next(
            item for item in categories.json() if item["name"] == "Groceries"
        )
        resp = await auth_client.put(
            f"/api/tools/expenses/categories/{groceries['id']}",
            json={"name": "Groceries", "monthly_budget": "500.00"},
        )
        assert resp.status_code == 200
        assert resp.json()["monthly_budget"] == "500.00"

    async def test_rename_updates_expenses(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        groceries = next(
            item for item in categories.json() if item["name"] == "Groceries"
        )
        await auth_client.put(
            f"/api/tools/expenses/categories/{groceries['id']}",
            json={"name": "Shopping"},
        )
        expenses = await auth_client.get("/api/tools/expenses")
        assert expenses.json()[0]["category"] == "Shopping"

    async def test_ensure_category_on_expense_create(self, db: AsyncSession):
        svc = ToolExpenseCategoryService(db)
        await svc.ensure_category("Custom")
        await db.commit()
        names = await svc.list_names()
        assert "Custom" in names
