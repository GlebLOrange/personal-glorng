"""Tests for TheMealDB recipe import helpers and seed command."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.db.documents.recipe import Recipe
from app.db.registry import DatabaseRegistry
from app.services.themealdb import (
    ThemealDBClient,
    map_meal_to_recipe,
    parse_ingredients,
    parse_steps,
)

SAMPLE_MEAL = {
    "idMeal": "52874",
    "strMeal": "Beef and Mustard Pie",
    "strCategory": "Beef",
    "strArea": "British",
    "strInstructions": (
        "Preheat the oven to 200C.\n"
        "Fry the beef until browned.\n"
        "Simmer the filling for 30 minutes."
    ),
    "strMealThumb": "https://www.themealdb.com/images/media/meals/example.jpg",
    "strYoutube": "https://www.youtube.com/watch?v=example",
    "strIngredient1": "Beef",
    "strMeasure1": "500g",
    "strIngredient2": "Mustard",
    "strMeasure2": "2 tbsp",
    "strIngredient3": "Onion",
    "strMeasure3": "1",
}


async def _seed_recipes_with_registry(
    registry: DatabaseRegistry,
    *,
    count: int,
    candidates: list[dict[str, object]],
) -> None:
    assert registry.recipes is not None
    existing_titles = {
        recipe.title for recipe in await registry.recipes.list(limit=10_000)
    }
    for data in candidates:
        if data["title"] in existing_titles:
            continue
        await registry.recipes.insert(
            Recipe(
                title=str(data["title"]),
                ingredients=json.dumps(data["ingredients"]),
                steps=json.dumps(data["steps"]),
                notes=data.get("notes"),  # type: ignore[arg-type]
                tags=json.dumps(data["tags"]),
                image_url=data.get("image_url"),  # type: ignore[arg-type]
                prep_time=data.get("prep_time"),  # type: ignore[arg-type]
                cook_time=data.get("cook_time"),  # type: ignore[arg-type]
                servings=data.get("servings"),  # type: ignore[arg-type]
            ),
        )
        existing_titles.add(str(data["title"]))


class TestThemealDBHelpers:
    def test_parse_ingredients(self) -> None:
        ingredients = parse_ingredients(SAMPLE_MEAL)
        assert ingredients == ["500g Beef", "2 tbsp Mustard", "1 Onion"]

    def test_parse_steps_splits_and_appends_multicooker_step(self) -> None:
        steps = parse_steps(SAMPLE_MEAL)
        assert steps[0] == "Preheat the oven to 200C."
        assert steps[-1] == (
            "Transfer to multicooker and cook on the appropriate program until done."
        )

    def test_map_meal_to_recipe(self) -> None:
        recipe = map_meal_to_recipe(SAMPLE_MEAL)
        assert recipe["title"] == "Beef and Mustard Pie"
        assert recipe["ingredients"]
        assert recipe["steps"]
        assert "multicooker" in recipe["tags"]
        assert "easy" in recipe["tags"]
        assert "themealdb" in recipe["tags"]
        assert recipe["cook_time"] == 30
        assert recipe["prep_time"] == 15
        assert recipe["image_url"] == SAMPLE_MEAL["strMealThumb"]
        assert "TheMealDB" in recipe["notes"]


class TestThemealDBClient:
    @pytest.mark.asyncio
    async def test_fetch_multicooker_candidates(self) -> None:
        client = ThemealDBClient()

        async def fake_get_json(
            path: str,
            params: dict[str, str] | None = None,
        ) -> dict:
            if path == "categories.php":
                return {"categories": [{"strCategory": "Beef"}]}
            if path == "filter.php":
                return {
                    "meals": [{"idMeal": "52874", "strMeal": "Beef and Mustard Pie"}]
                }
            if path == "lookup.php":
                return {"meals": [SAMPLE_MEAL]}
            msg = f"Unexpected path: {path}"
            raise AssertionError(msg)

        with patch.object(client, "_get_json", side_effect=fake_get_json):
            recipes = await client.fetch_multicooker_candidates(limit=1)

        assert len(recipes) == 1
        assert recipes[0]["title"] == "Beef and Mustard Pie"


class TestSeedMulticookerRecipes:
    @pytest.mark.asyncio
    @patch("app.db.seed_multicooker_recipes.ThemealDBClient")
    async def test_skips_existing_titles(
        self,
        mock_client_cls: MagicMock,
        registry: DatabaseRegistry,
    ) -> None:
        assert registry.recipes is not None
        await registry.recipes.insert(
            Recipe(
                title="Beef and Mustard Pie",
                ingredients=json.dumps(["existing"]),
                steps=json.dumps(["existing step"]),
                tags=json.dumps(["existing"]),
            ),
        )

        mock_client = mock_client_cls.return_value
        mock_client.fetch_multicooker_candidates = AsyncMock(
            return_value=[map_meal_to_recipe(SAMPLE_MEAL)]
        )

        await _seed_recipes_with_registry(
            registry,
            count=1,
            candidates=await mock_client.fetch_multicooker_candidates(limit=1),
        )

        count = await registry.recipes.count()
        assert count == 1

    @pytest.mark.asyncio
    @patch("app.db.seed_multicooker_recipes.ThemealDBClient")
    async def test_inserts_new_recipes(
        self,
        mock_client_cls: MagicMock,
        registry: DatabaseRegistry,
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.fetch_multicooker_candidates = AsyncMock(
            return_value=[map_meal_to_recipe(SAMPLE_MEAL)]
        )

        candidates = await mock_client.fetch_multicooker_candidates(limit=1)
        await _seed_recipes_with_registry(registry, count=1, candidates=candidates)

        assert registry.recipes is not None
        recipes = await registry.recipes.list(limit=10)
        recipe = next(item for item in recipes if item.title == "Beef and Mustard Pie")
        assert json.loads(recipe.tags) == map_meal_to_recipe(SAMPLE_MEAL)["tags"]
