from httpx import AsyncClient

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
    async def test_requires_auth(self, client: AsyncClient):
        resp = await client.get("/api/tools/recipes")
        assert resp.status_code == 401

    async def test_create_recipe(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Pasta Carbonara"
        assert data["tags"] == ["italian", "quick"]
        assert data["servings"] == 2

    async def test_list_recipes(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        resp = await auth_client.get("/api/tools/recipes")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

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

    async def test_search_by_title(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        await auth_client.post("/api/tools/recipes", json={
            **RECIPE_DATA, "title": "Risotto", "tags": ["italian"],
        })
        resp = await auth_client.get("/api/tools/recipes?search=carbo")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["title"] == "Pasta Carbonara"

    async def test_filter_by_tag(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        await auth_client.post("/api/tools/recipes", json={
            **RECIPE_DATA, "title": "Salad", "tags": ["healthy"],
        })
        resp = await auth_client.get("/api/tools/recipes?tag=quick")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    async def test_list_tags(self, auth_client: AsyncClient):
        await auth_client.post("/api/tools/recipes", json=RECIPE_DATA)
        resp = await auth_client.get("/api/tools/recipes/tags")
        assert resp.status_code == 200
        tags = resp.json()
        assert "italian" in tags
        assert "quick" in tags

    async def test_create_missing_title(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tools/recipes", json={
            "ingredients": ["a"], "steps": ["b"],
        })
        assert resp.status_code == 422

    async def test_create_empty_ingredients(self, auth_client: AsyncClient):
        resp = await auth_client.post("/api/tools/recipes", json={
            "title": "Empty", "ingredients": [], "steps": ["cook"],
        })
        assert resp.status_code == 422
