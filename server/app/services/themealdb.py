"""Fetch and map recipes from TheMealDB public API."""

import re
from typing import Any

import httpx

from app.core.logging import logger

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = 15.0
MULTICOOKER_CATEGORIES = (
    "Beef",
    "Chicken",
    "Pasta",
    "Pork",
    "Vegetarian",
    "Side",
    "Soup",
)
MULTICOOKER_KEYWORDS = (
    "stew",
    "soup",
    "simmer",
    "pressure",
    "slow cook",
    "slow-cook",
    "braise",
)
STEP_SPLIT_RE = re.compile(
    r"(?:\r?\n|\.\s+(?=\d+\.)|(?<=\.)\s*(?=STEP\s+\d+))",
    re.IGNORECASE,
)
NUMBERED_STEP_RE = re.compile(r"^\s*(?:STEP\s+)?\d+[.)]\s*", re.IGNORECASE)
COOK_TIME_RE = re.compile(r"(\d+)\s*(?:min(?:ute)?s?|hour?s?|hrs?)", re.IGNORECASE)
MULTICOOKER_FINAL_STEP = (
    "Transfer to multicooker and cook on the appropriate program until done."
)


def parse_ingredients(meal: dict[str, Any]) -> list[str]:
    """Build ingredient lines from TheMealDB strIngredient/strMeasure fields."""
    ingredients: list[str] = []
    for index in range(1, 21):
        ingredient = (meal.get(f"strIngredient{index}") or "").strip()
        if not ingredient:
            continue
        measure = (meal.get(f"strMeasure{index}") or "").strip()
        ingredients.append(f"{measure} {ingredient}".strip() if measure else ingredient)
    return ingredients


def parse_steps(meal: dict[str, Any]) -> list[str]:
    """Split meal instructions into discrete steps."""
    instructions = (meal.get("strInstructions") or "").strip()
    if not instructions:
        return [MULTICOOKER_FINAL_STEP]

    raw_parts = [
        part.strip() for part in STEP_SPLIT_RE.split(instructions) if part.strip()
    ]
    steps = [NUMBERED_STEP_RE.sub("", part).strip() for part in raw_parts]
    steps = [step for step in steps if step]
    if not steps:
        steps = [instructions]
    if steps[-1] != MULTICOOKER_FINAL_STEP:
        steps.append(MULTICOOKER_FINAL_STEP)
    return steps


def parse_cook_time_minutes(meal: dict[str, Any]) -> int:
    """Extract the longest cook duration mentioned in instructions."""
    instructions = meal.get("strInstructions") or ""
    max_minutes = 0
    for match in COOK_TIME_RE.finditer(instructions):
        value = int(match.group(1))
        unit = match.group(0).lower()
        minutes = value * 60 if "hour" in unit or "hr" in unit else value
        max_minutes = max(max_minutes, minutes)
    return max_minutes or 60


def build_tags(meal: dict[str, Any]) -> list[str]:
    """Build deduplicated lowercase tags for a mapped recipe."""
    tags = ["multicooker", "easy", "themealdb"]
    for key in ("strCategory", "strArea"):
        value = (meal.get(key) or "").strip().lower()
        if value:
            tags.append(value)
    seen: set[str] = set()
    deduped: list[str] = []
    for tag in tags:
        if tag not in seen:
            seen.add(tag)
            deduped.append(tag)
    return deduped


def build_notes(meal: dict[str, Any]) -> str:
    """Build source notes with optional YouTube link."""
    notes = "Imported from TheMealDB for multicooker testing."
    youtube = (meal.get("strYoutube") or "").strip()
    if youtube:
        notes = f"{notes} Video: {youtube}"
    return notes


def score_meal_for_easiness(meal: dict[str, Any]) -> tuple[int, int, int]:
    """Return a sort key where lower values mean easier and more suitable."""
    ingredient_count = len(parse_ingredients(meal))
    instruction_length = len(meal.get("strInstructions") or "")
    instructions_lower = (meal.get("strInstructions") or "").lower()
    keyword_bonus = (
        -10
        if any(keyword in instructions_lower for keyword in MULTICOOKER_KEYWORDS)
        else 0
    )
    return (
        ingredient_count,
        instruction_length + keyword_bonus,
        int(meal.get("idMeal") or 0),
    )


def map_meal_to_recipe(meal: dict[str, Any]) -> dict[str, Any]:
    """Map a TheMealDB meal payload to the seed recipe dict shape."""
    title = (meal.get("strMeal") or "Untitled Recipe").strip()[:255]
    ingredients = parse_ingredients(meal)
    steps = parse_steps(meal)
    if not ingredients:
        msg = f"Meal '{title}' has no ingredients"
        raise ValueError(msg)

    return {
        "title": title,
        "ingredients": ingredients,
        "steps": steps,
        "notes": build_notes(meal),
        "tags": build_tags(meal),
        "image_url": (meal.get("strMealThumb") or "").strip() or None,
        "prep_time": 15,
        "cook_time": parse_cook_time_minutes(meal),
        "servings": None,
    }


class ThemealDBClient:
    """Client for TheMealDB free V1 API."""

    def __init__(self, base_url: str = BASE_URL, timeout: float = TIMEOUT) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def _get_json(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error(
                "TheMealDB request failed",
                context={"url": url, "error": str(exc)},
            )
            raise RuntimeError(f"TheMealDB request failed for {url}") from exc

        payload = response.json()
        if not isinstance(payload, dict):
            msg = f"TheMealDB returned invalid JSON for {url}"
            raise RuntimeError(msg)
        return payload

    async def list_categories(self) -> list[str]:
        """Return available meal category names."""
        payload = await self._get_json("categories.php")
        categories = payload.get("categories") or []
        return [
            str(item.get("strCategory")).strip()
            for item in categories
            if isinstance(item, dict) and item.get("strCategory")
        ]

    async def filter_by_category(self, category: str) -> list[dict[str, Any]]:
        """Return meal stubs for a category."""
        payload = await self._get_json("filter.php", params={"c": category})
        meals = payload.get("meals") or []
        return [meal for meal in meals if isinstance(meal, dict)]

    async def lookup_meal(self, meal_id: str) -> dict[str, Any] | None:
        """Return full meal details for an ID."""
        payload = await self._get_json("lookup.php", params={"i": meal_id})
        meals = payload.get("meals") or []
        if not meals:
            return None
        meal = meals[0]
        return meal if isinstance(meal, dict) else None

    async def fetch_multicooker_candidates(
        self,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        """Fetch and rank easy multicooker-friendly recipes."""
        if limit < 1:
            msg = "limit must be at least 1"
            raise ValueError(msg)

        available_categories = set(await self.list_categories())
        categories = [
            name for name in MULTICOOKER_CATEGORIES if name in available_categories
        ]
        if not categories:
            msg = "No multicooker categories found in TheMealDB"
            raise RuntimeError(msg)

        meal_ids: list[str] = []
        seen_ids: set[str] = set()
        for category in categories:
            for stub in await self.filter_by_category(category):
                meal_id = str(stub.get("idMeal") or "").strip()
                if not meal_id or meal_id in seen_ids:
                    continue
                seen_ids.add(meal_id)
                meal_ids.append(meal_id)

        ranked_meals: list[dict[str, Any]] = []
        for meal_id in meal_ids:
            meal = await self.lookup_meal(meal_id)
            if meal is None:
                continue
            try:
                map_meal_to_recipe(meal)
            except ValueError:
                continue
            ranked_meals.append(meal)

        ranked_meals.sort(key=score_meal_for_easiness)
        mapped: list[dict[str, Any]] = []
        seen_titles: set[str] = set()
        for meal in ranked_meals:
            recipe = map_meal_to_recipe(meal)
            if recipe["title"] in seen_titles:
                continue
            seen_titles.add(recipe["title"])
            mapped.append(recipe)
            if len(mapped) >= limit:
                break

        if not mapped:
            msg = "TheMealDB returned no usable multicooker recipes"
            raise RuntimeError(msg)

        return mapped
