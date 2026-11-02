from httpx import AsyncClient

from app.db.registry import DatabaseRegistry
from app.services.expense_category import ExpenseCategoryService

EXPENSE_DATA = {
    "tool_name": "Milk",
    "amount": "5.00",
    "currency": "PLN",
    "expense_date": "2025-03-15",
    "category": "Food",
    "notes": None,
}

STARTER_NAMES = {
    "Food",
    "Home & bills",
    "Transport",
    "Health",
    "Personal",
    "Entertainment",
    "Other",
}


class TestExpenseCategories:
    async def test_list_default_categories(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/tools/expenses/categories")
        assert resp.status_code == 200
        names = {item["name"] for item in resp.json()}
        assert STARTER_NAMES.issubset(names)

    async def test_deleted_starter_does_not_return(self, auth_client: AsyncClient):
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        delete_resp = await auth_client.delete(
            f"/api/tools/expenses/categories/{food['id']}",
        )
        assert delete_resp.status_code == 204

        relist = await auth_client.get("/api/tools/expenses/categories")
        names = {item["name"] for item in relist.json()}
        assert "Food" not in names

    async def test_create_and_rename_category(self, auth_client: AsyncClient):
        create_resp = await auth_client.post(
            "/api/tools/expenses/categories",
            json={"name": "Pets"},
        )
        assert create_resp.status_code == 201
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
        assert delete_resp.status_code == 204

    async def test_cannot_delete_category_in_use_without_replacement(
        self,
        auth_client: AsyncClient,
    ):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        delete_resp = await auth_client.delete(
            f"/api/tools/expenses/categories/{food['id']}",
        )
        assert delete_resp.status_code == 422

    async def test_delete_category_reassigns_to_other(
        self,
        auth_client: AsyncClient,
    ):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        transport = next(
            item for item in categories.json() if item["name"] == "Transport"
        )
        delete_resp = await auth_client.request(
            "DELETE",
            f"/api/tools/expenses/categories/{food['id']}",
            json={"replacement_category_id": transport["id"]},
        )
        assert delete_resp.status_code == 204

        expenses = await auth_client.get("/api/tools/expenses")
        assert expenses.json()["items"][0]["category"] == "Transport"

        relist = await auth_client.get("/api/tools/expenses/categories")
        names = {item["name"] for item in relist.json()}
        assert "Food" not in names

    async def test_delete_category_to_uncategorized(
        self,
        auth_client: AsyncClient,
    ):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        delete_resp = await auth_client.request(
            "DELETE",
            f"/api/tools/expenses/categories/{food['id']}",
            json={"replacement_category_id": None},
        )
        assert delete_resp.status_code == 204

        expenses = await auth_client.get("/api/tools/expenses")
        assert expenses.json()["items"][0]["category"] is None

    async def test_delete_category_rejects_self_reassignment(
        self,
        auth_client: AsyncClient,
    ):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        delete_resp = await auth_client.request(
            "DELETE",
            f"/api/tools/expenses/categories/{food['id']}",
            json={"replacement_category_id": food["id"]},
        )
        assert delete_resp.status_code == 422

    async def test_delete_category_rejects_unknown_replacement(
        self,
        auth_client: AsyncClient,
    ):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        delete_resp = await auth_client.request(
            "DELETE",
            f"/api/tools/expenses/categories/{food['id']}",
            json={"replacement_category_id": 999999},
        )
        assert delete_resp.status_code in {404, 422}

    async def test_update_category_budget(self, auth_client: AsyncClient):
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        resp = await auth_client.put(
            f"/api/tools/expenses/categories/{food['id']}",
            json={"name": "Food", "monthly_budget": "500.00"},
        )
        assert resp.status_code == 200
        assert resp.json()["monthly_budget"] == "500.00"

    async def test_rename_updates_expenses(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/expenses", json=EXPENSE_DATA)
        categories = await auth_client.get("/api/tools/expenses/categories")
        food = next(item for item in categories.json() if item["name"] == "Food")
        await auth_client.put(
            f"/api/tools/expenses/categories/{food['id']}",
            json={"name": "Shopping"},
        )
        expenses = await auth_client.get("/api/tools/expenses")
        assert expenses.json()["items"][0]["category"] == "Shopping"

    async def test_ensure_category_on_expense_create(self, registry: DatabaseRegistry):
        svc = ExpenseCategoryService(registry)
        await svc.ensure_category("Custom")
        names = await svc.list_names()
        assert "Custom" in names

    async def test_ensure_defaults_is_one_time(self, registry: DatabaseRegistry):
        svc = ExpenseCategoryService(registry)
        await svc.ensure_defaults()
        first = await svc.list_names()
        assert "Food" in first

        food = next(c for c in await svc.list_categories() if c.name == "Food")
        await svc.delete_category(food.id)
        await svc.ensure_defaults()
        names = await svc.list_names()
        assert "Food" not in names
