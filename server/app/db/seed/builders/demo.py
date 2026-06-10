"""Factories for demo seed data (stdlib random, no Faker).

Moved from ``app.db.seed.demo_builders``.
"""

import json
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.core.permissions import permission_key
from app.db.documents.feedback import Feedback
from app.db.documents.recipe import Recipe
from app.db.documents.task import Task, TaskStatus
from app.platform.registry import PLATFORM_SERVICES

DEMO_READER_EMAIL = "demo.reader@random.oi"
DEMO_WRITER_EMAIL = "demo.writer@random.oi"

TAG_ADJECTIVES = (
    "quick",
    "easy",
    "healthy",
    "comfort",
    "spicy",
    "mild",
    "creamy",
    "crispy",
    "fresh",
    "hearty",
    "light",
    "rich",
    "smoky",
    "tangy",
    "sweet",
    "savory",
    "seasonal",
    "weeknight",
    "weekend",
    "budget",
)
TAG_CUISINES = (
    "italian",
    "mexican",
    "indian",
    "thai",
    "japanese",
    "korean",
    "french",
    "greek",
    "american",
    "british",
    "middle-eastern",
    "vietnamese",
    "spanish",
    "turkish",
    "polish",
)
TAG_TYPES = (
    "breakfast",
    "lunch",
    "dinner",
    "dessert",
    "soup",
    "salad",
    "pasta",
    "grill",
    "bake",
    "stew",
    "curry",
    "snack",
    "appetizer",
    "side",
    "one-pot",
)
TAG_PROTEINS = (
    "chicken",
    "beef",
    "pork",
    "fish",
    "seafood",
    "tofu",
    "vegetarian",
    "vegan",
    "eggs",
    "lamb",
)

RECIPE_ADJECTIVES = ("Classic", "Homestyle", "Rustic", "Spicy", "Creamy", "Fresh")
RECIPE_PROTEINS = ("Chicken", "Beef", "Salmon", "Tofu", "Shrimp", "Pork", "Lamb")
RECIPE_STYLES = (
    "Stir-Fry",
    "Curry",
    "Soup",
    "Salad",
    "Pasta",
    "Bowl",
    "Tacos",
    "Skillet",
)
INGREDIENTS = (
    "onion",
    "garlic",
    "olive oil",
    "salt",
    "pepper",
    "tomatoes",
    "bell pepper",
    "carrots",
    "potatoes",
    "rice",
    "pasta",
    "lemon",
    "butter",
    "cream",
    "soy sauce",
    "cilantro",
    "parsley",
    "ginger",
    "chili flakes",
    "cheese",
)
STEP_TEMPLATES = (
    "Prep ingredients and heat the pan.",
    "Sauté aromatics until fragrant.",
    "Add main ingredients and season well.",
    "Simmer until tender and flavors combine.",
    "Adjust seasoning and serve warm.",
    "Garnish and plate immediately.",
)

FEEDBACK_THEMES = (
    "Bug report",
    "Feature request",
    "General feedback",
    "UI improvement",
    "Performance",
    "Content suggestion",
    "Accessibility",
    "Mobile experience",
)
FEEDBACK_MESSAGES = (
    "Love the new layout — very clean and fast.",
    "Found a small typo on the recipes page.",
    "Would be great to export expenses as CSV.",
    "Task reminders sometimes arrive a bit late.",
    "Short links work perfectly, thanks!",
    "Dark mode contrast could be improved in the admin panel.",
    "The calculator tool is super handy on mobile.",
    "Please add bulk delete for feedback items.",
)
FEEDBACK_STATUSES = ("unread", "unread", "unread", "read", "read", "archived")

TASK_TITLES = (
    "Review PR",
    "Call dentist",
    "Buy groceries",
    "Write blog post",
    "Sync calendar",
    "Pay invoices",
    "Gym session",
    "Fix nginx config",
    "Reply to feedback",
    "Plan sprint",
    "Water plants",
    "Book flights",
    "Update dependencies",
    "Team standup",
    "Prepare presentation",
)

WRITER_TOOL_SLUGS = frozenset(
    {"recipes", "expenses", "tasks", "url-shortener", "feedback"},
)

SHORT_URL_TARGETS = (
    "https://example.com/docs/getting-started",
    "https://github.com/glorng/portfolio",
    "https://developer.mozilla.org/en-US/docs/Web",
    "https://fastapi.tiangolo.com/",
    "https://vuejs.org/guide/introduction.html",
    "https://www.postgresql.org/docs/",
    "https://redis.io/docs/latest/",
    "https://docs.docker.com/compose/",
)


def demo_reader_permissions() -> list[str]:
    """Read access for every registry capability named read."""
    perms: list[str] = []
    for service in PLATFORM_SERVICES:
        if "read" in service.capabilities:
            perms.append(permission_key(service.slug, "read"))
    return perms


def demo_writer_permissions() -> list[str]:
    """Read + write on productivity/content tools (no superuser)."""
    perms: list[str] = []
    for service in PLATFORM_SERVICES:
        if service.slug not in WRITER_TOOL_SLUGS:
            continue
        for cap in ("read", "write"):
            if cap in service.capabilities:
                perms.append(permission_key(service.slug, cap))
    return perms


def build_recipe_tag_pool(count: int, *, seed: int = 42) -> list[str]:
    """Build a pool of unique recipe tag strings."""
    rng = random.Random(seed)  # noqa: S311
    pool: list[str] = []
    seen: set[str] = set()
    sources = (TAG_ADJECTIVES, TAG_CUISINES, TAG_TYPES, TAG_PROTEINS)
    attempt = 0
    while len(pool) < count and attempt < count * 10:
        attempt += 1
        parts = [rng.choice(source) for source in sources]
        tag = "-".join(parts[: rng.randint(1, 2)])
        if tag in seen:
            tag = f"{tag}-{len(seen) + 1}"
        if tag not in seen:
            seen.add(tag)
            pool.append(tag)
    while len(pool) < count:
        tag = f"tag-{len(pool) + 1}"
        if tag not in seen:
            seen.add(tag)
            pool.append(tag)
    return pool


def build_random_recipes(
    count: int,
    tag_pool: list[str],
    *,
    seed: int = 42,
) -> list[Recipe]:
    """Build procedurally generated recipe rows."""
    rng = random.Random(seed)  # noqa: S311
    rows: list[Recipe] = []
    for index in range(count):
        title = (
            f"{rng.choice(RECIPE_ADJECTIVES)} "
            f"{rng.choice(RECIPE_PROTEINS)} "
            f"{rng.choice(RECIPE_STYLES)} #{index + 1}"
        )
        ingredient_count = rng.randint(4, 8)
        ingredients = rng.sample(INGREDIENTS, k=min(ingredient_count, len(INGREDIENTS)))
        step_count = rng.randint(3, 6)
        steps = [rng.choice(STEP_TEMPLATES) for _ in range(step_count)]
        tag_count = rng.randint(2, 4)
        tags = rng.sample(tag_pool, k=min(tag_count, len(tag_pool)))
        rows.append(
            Recipe(
                title=title,
                ingredients=json.dumps(ingredients),
                steps=json.dumps(steps),
                tags=json.dumps(tags),
                prep_time=rng.randint(5, 45),
                cook_time=rng.randint(0, 90),
                servings=rng.randint(1, 8),
            ),
        )
    return rows


def build_random_feedback(count: int, *, seed: int = 42) -> list[Feedback]:
    """Build feedback rows with mixed statuses."""
    rng = random.Random(seed)  # noqa: S311
    rows: list[Feedback] = []
    for index in range(count):
        rows.append(
            Feedback(
                email=f"user{index + 1}@example.com",
                theme=rng.choice(FEEDBACK_THEMES),
                message=rng.choice(FEEDBACK_MESSAGES),
                status=rng.choice(FEEDBACK_STATUSES),
            ),
        )
    return rows


def build_random_tasks(
    count: int,
    *,
    telegram_user_id: int,
    timezone: str,
    seed: int = 42,
) -> list[Task]:
    """Build tasks spanning the last 30 days and next 7 days."""
    rng = random.Random(seed)  # noqa: S311
    tz = ZoneInfo(timezone)
    now_local = datetime.now(tz)
    start = now_local - timedelta(days=30)
    end = now_local + timedelta(days=7)
    span_seconds = max(int((end - start).total_seconds()), 1)
    statuses = [
        TaskStatus.PENDING,
        TaskStatus.COMPLETED,
        TaskStatus.POSTPONED,
        TaskStatus.NOT_COMPLETED,
        TaskStatus.CANCELLED,
    ]
    rows: list[Task] = []
    for _ in range(count):
        offset = rng.randint(0, span_seconds)
        scheduled = (start + timedelta(seconds=offset)).astimezone(UTC)
        rows.append(
            Task(
                telegram_user_id=telegram_user_id,
                title=rng.choice(TASK_TITLES),
                description=rng.choice([None, "Demo task description"]),
                location=rng.choice([None, "Home", "Office", "Gym"]),
                scheduled_at=scheduled,
                status=rng.choice(statuses),
            ),
        )
    return rows


@dataclass(frozen=True)
class ShortUrlSeed:
    """Payload for creating a demo short URL."""

    original_url: str
    title: str | None
    clicks: int


def build_short_url_seeds(count: int, *, seed: int = 42) -> list[ShortUrlSeed]:
    """Build short URL creation payloads."""
    rng = random.Random(seed)  # noqa: S311
    rows: list[ShortUrlSeed] = []
    for index in range(count):
        base = rng.choice(SHORT_URL_TARGETS)
        rows.append(
            ShortUrlSeed(
                original_url=f"{base}?demo={index + 1}",
                title=f"Demo link {index + 1}",
                clicks=rng.randint(0, 500),
            ),
        )
    return rows
