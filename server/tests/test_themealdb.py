"""Tests for TheMealDB recipe import helpers and seed command."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.recipe import Recipe
from app.db.seed_multicooker_recipes import seed_multicooker_recipes
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


def _session_ctx(db: AsyncSession) -> callable:
    """Build a fake session factory that yields the test db session."""

    @asynccontextmanager
    async def _ctx() -> AsyncGenerator[AsyncSession]:
        yield db

    return _ctx


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
    @patch("app.db.seed_multicooker_recipes.get_session_factory")
    @patch("app.db.seed_multicooker_recipes.ThemealDBClient")
    async def test_skips_existing_titles(
        self,
        mock_client_cls: MagicMock,
        mock_factory: MagicMock,
        db: AsyncSession,
    ) -> None:
        db.add(
            Recipe(
                title="Beef and Mustard Pie",
                ingredients=json.dumps(["existing"]),
                steps=json.dumps(["existing step"]),
                tags=json.dumps(["existing"]),
            )
        )
        await db.commit()

        mock_client = mock_client_cls.return_value
        mock_client.fetch_multicooker_candidates = AsyncMock(
            return_value=[map_meal_to_recipe(SAMPLE_MEAL)]
        )
        mock_factory.return_value = _session_ctx(db)

        await seed_multicooker_recipes(count=1)

        count = await db.scalar(select(func.count()).select_from(Recipe))
        assert count == 1

    @pytest.mark.asyncio
    @patch("app.db.seed_multicooker_recipes.get_session_factory")
    @patch("app.db.seed_multicooker_recipes.ThemealDBClient")
    async def test_inserts_new_recipes(
        self,
        mock_client_cls: MagicMock,
        mock_factory: MagicMock,
        db: AsyncSession,
    ) -> None:
        mock_client = mock_client_cls.return_value
        mock_client.fetch_multicooker_candidates = AsyncMock(
            return_value=[map_meal_to_recipe(SAMPLE_MEAL)]
        )
        mock_factory.return_value = _session_ctx(db)

        await seed_multicooker_recipes(count=1)

        result = await db.execute(
            select(Recipe).where(Recipe.title == "Beef and Mustard Pie")
        )
        recipe = result.scalar_one()
        assert json.loads(recipe.tags) == map_meal_to_recipe(SAMPLE_MEAL)["tags"]
