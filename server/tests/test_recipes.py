from httpx import AsyncClient

from app.db.documents.user import User
from app.db.registry import DatabaseRegistry

RECIPE_DATA = {
    "title": "Pasta Carbonara",
    "ingredients": ["pasta", "eggs", "parmesan", "pancetta"],
    "steps": ["Boil pasta", "Fry pancetta", "Mix eggs with cheese", "Combine"],
    "tags": ["italian", "quick"],
    "prep_time": 10,
    "cook_time": 20,
    "servings": 2,
}


class TestRecipesCRUD:
    async def test_public_read_list(self, client: AsyncClient):
        resp = await client.get("/api/tools/recipes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["items"] == []
        assert data["total"] == 0

    async def test_create_requires_auth(self, client: AsyncClient):
        resp = await client.post("/api/tools/recipes", json=RECIPE_DATA)
        assert resp.status_code == 401

    async def test_create_recipe(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Pasta Carbonara"
        assert data["tags"] == ["italian", "quick"]
        assert data["servings"] == 2

    async def test_create_recipe_sanitizes_title_and_ingredients(
        self, auth_client: AsyncClient
    ):
        payload = {
            **RECIPE_DATA,
            "title": "  Pasta\x00 Carbonara  ",
            "ingredients": ["  eggs\x00  ", "pasta"],
        }
        resp = await auth_client.post("/api/tools/recipes", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Pasta Carbonara"
        assert data["ingredients"] == ["eggs", "pasta"]

    async def test_list_recipes(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        resp = await auth_client.get("/api/tools/recipes")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["page"] == 1
        assert data["per_page"] == 9

    async def test_get_recipe(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        recipe_id = create_resp.json()["id"]
        resp = await auth_client.get(f"/api/tools/recipes/{recipe_id}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Pasta Carbonara"

    async def test_update_recipe(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        recipe_id = create_resp.json()["id"]
        resp = await auth_client.put(
            f"/api/tools/recipes/{recipe_id}",
            json={"title": "Updated Carbonara", "servings": 4},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Updated Carbonara"
        assert data["servings"] == 4

    async def test_delete_recipe(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        recipe_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/tools/recipes/{recipe_id}")
        assert resp.status_code == 200

        get_resp = await auth_client.get(f"/api/tools/recipes/{recipe_id}")
        assert get_resp.status_code == 404
        assert "not found" in get_resp.json()["detail"].lower()

    async def test_get_recipe_not_found(self, auth_client: AsyncClient):
        resp = await auth_client.get("/api/tools/recipes/99999")
        assert resp.status_code == 404
        assert "not found" in resp.json()["detail"].lower()

    async def test_update_empty_ingredients(self, auth_client: AsyncClient):
        create_resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        recipe_id = create_resp.json()["id"]
        resp = await auth_client.put(
            f"/api/tools/recipes/{recipe_id}",
            json={"ingredients": []},
        )
        assert resp.status_code == 422

    async def test_create_records_audit_actor(
        self,
        auth_client: AsyncClient,
        registry: DatabaseRegistry,
        admin_user: User,
    ):
        resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        assert resp.status_code == 200
        recipe_id = resp.json()["id"]

        row = await registry.mongo_db.audit_events.find_one(
            {"action": "recipe.created", "resource_id": recipe_id},
        )
        assert row is not None
        assert row["actor_id"] == admin_user.id

    async def test_delete_records_audit_actor(
        self,
        auth_client: AsyncClient,
        registry: DatabaseRegistry,
        admin_user: User,
    ):
        create_resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        recipe_id = create_resp.json()["id"]
        resp = await auth_client.delete(f"/api/tools/recipes/{recipe_id}")
        assert resp.status_code == 200

        row = await registry.mongo_db.audit_events.find_one(
            {"action": "recipe.deleted", "resource_id": recipe_id},
        )
        assert row is not None
        assert row["actor_id"] == admin_user.id

    async def test_search_by_title(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        await auth_client.post(
            "/api/tools/recipes",
            json={
                **RECIPE_DATA,
                "title": "Risotto",
                "tags": ["italian"],
            },
        )
        resp = await auth_client.get("/api/tools/recipes?search=carbo")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Pasta Carbonara"

    async def test_search_by_ingredient(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        await auth_client.post(
            "/api/tools/recipes",
            json={
                **RECIPE_DATA,
                "title": "Plain Rice",
                "ingredients": ["rice", "water"],
                "steps": ["Boil rice"],
            },
        )
        resp = await auth_client.get("/api/tools/recipes?search=pancetta")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 1
        assert data["items"][0]["title"] == "Pasta Carbonara"

    async def test_filter_by_tag(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        await auth_client.post(
            "/api/tools/recipes",
            json={
                **RECIPE_DATA,
                "title": "Salad",
                "tags": ["healthy"],
            },
        )
        resp = await auth_client.get("/api/tools/recipes?tag=quick")
        assert resp.status_code == 200
        assert resp.json()["total"] == 1

    async def test_list_tags(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        resp = await auth_client.get("/api/tools/recipes/tags")
        assert resp.status_code == 200
        tags = resp.json()
        assert "italian" in tags
        assert "quick" in tags

    async def test_create_missing_title(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/tools/recipes",
            json={
                "ingredients": ["a"],
                "steps": ["b"],
            },
        )
        assert resp.status_code == 422

    async def test_create_empty_ingredients(self, auth_client: AsyncClient):
        resp = await auth_client.post(
            "/api/tools/recipes",
            json={
                "title": "Empty",
                "ingredients": [],
                "steps": ["cook"],
            },
        )
        assert resp.status_code == 422


class TestRecipesList:
    async def test_pagination(self, auth_client: AsyncClient):
        for i in range(3):
            await auth_client.post(
                "/api/tools/recipes",
                json={**RECIPE_DATA, "title": f"Recipe {i}"},
            )
        resp = await auth_client.get("/api/tools/recipes?page=1&per_page=2")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["pages"] == 2

        page2 = await auth_client.get("/api/tools/recipes?page=2&per_page=2")
        assert len(page2.json()["items"]) == 1

    async def test_sort_title_asc(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/tools/recipes",
            json={**RECIPE_DATA, "title": "Zucchini Soup"},
        )
        await auth_client.post(
            "/api/tools/recipes",
            json={**RECIPE_DATA, "title": "Apple Pie"},
        )
        resp = await auth_client.get("/api/tools/recipes?sort=title_asc")
        titles = [item["title"] for item in resp.json()["items"]]
        assert titles == sorted(titles)

    async def test_sort_prep_asc(self, auth_client: AsyncClient):
        await auth_client.post(
            "/api/tools/recipes",
            json={**RECIPE_DATA, "title": "Slow", "prep_time": 60},
        )
        await auth_client.post(
            "/api/tools/recipes",
            json={**RECIPE_DATA, "title": "Fast", "prep_time": 5},
        )
        resp = await auth_client.get("/api/tools/recipes?sort=prep_asc")
        titles = [item["title"] for item in resp.json()["items"]]
        assert titles[0] == "Fast"
