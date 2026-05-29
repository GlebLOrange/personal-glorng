"""Seed script to create admin user and sample recipes."""

import json
import random

from sqlalchemy import func, select

from app.core.logging import logger
from app.db.models.audit_event import AuditActorType, AuditSource
from app.db.models.recipe import Recipe
from app.db.models.task import Task
from app.db.models.tool_expense import ToolExpense
from app.db.models.user import User
from app.db.seed.builders import build_random_expenses, build_tasks_for_today
from app.db.session import get_session_factory
from app.services.task import TaskService
from app.services.tool_expense_category import ToolExpenseCategoryService
from app.services.user import create_user, default_owner_permissions
from app.settings import get_settings

WEAK_PASSWORDS = {"changeme", "password", "admin", "123456", "secret"}

SAMPLE_RECIPES: list[dict] = [
    {
        "title": "Classic Margherita Pizza",
        "ingredients": [
            "pizza dough",
            "San Marzano tomatoes",
            "fresh mozzarella",
            "basil",
            "olive oil",
            "salt",
        ],
        "steps": [
            "Preheat oven to 250°C.",
            "Roll out dough on a floured surface.",
            "Spread crushed tomatoes evenly.",
            "Add torn mozzarella pieces.",
            "Bake 10-12 min until crust is golden.",
            "Top with fresh basil and a drizzle of olive oil.",
        ],
        "tags": ["italian", "vegetarian", "pizza"],
        "prep_time": 20,
        "cook_time": 12,
        "servings": 4,
    },
    {
        "title": "Chicken Tikka Masala",
        "ingredients": [
            "chicken thighs",
            "yogurt",
            "garam masala",
            "cumin",
            "tomato sauce",
            "cream",
            "onion",
            "garlic",
            "ginger",
            "cilantro",
        ],
        "steps": [
            "Marinate chicken in yogurt and spices for 1 hour.",
            "Grill or broil chicken until charred.",
            "Sauté onion, garlic, and ginger.",
            "Add tomato sauce and simmer 15 min.",
            "Stir in cream and cooked chicken.",
            "Garnish with cilantro and serve with rice.",
        ],
        "tags": ["indian", "chicken", "curry"],
        "prep_time": 70,
        "cook_time": 30,
        "servings": 4,
    },
    {
        "title": "Japanese Miso Ramen",
        "ingredients": [
            "ramen noodles",
            "miso paste",
            "chicken broth",
            "soy sauce",
            "sesame oil",
            "soft-boiled egg",
            "chashu pork",
            "green onion",
            "nori",
        ],
        "steps": [
            "Boil noodles according to package.",
            "Heat broth and whisk in miso paste.",
            "Season with soy sauce and sesame oil.",
            "Assemble bowls: noodles, broth, toppings.",
            "Add halved soft-boiled egg, pork slices, green onion, and nori.",
        ],
        "tags": ["japanese", "soup", "pork"],
        "prep_time": 15,
        "cook_time": 25,
        "servings": 2,
    },
    {
        "title": "Beef Tacos",
        "ingredients": [
            "ground beef",
            "taco shells",
            "lettuce",
            "tomato",
            "cheddar cheese",
            "sour cream",
            "cumin",
            "chili powder",
            "onion",
            "garlic",
        ],
        "steps": [
            "Brown ground beef with diced onion and garlic.",
            "Season with cumin and chili powder.",
            "Warm taco shells in oven.",
            "Fill shells with beef, lettuce, tomato, and cheese.",
            "Top with sour cream.",
        ],
        "tags": ["mexican", "beef", "quick"],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 4,
    },
    {
        "title": "Greek Salad",
        "ingredients": [
            "cucumber",
            "tomatoes",
            "red onion",
            "kalamata olives",
            "feta cheese",
            "olive oil",
            "red wine vinegar",
            "oregano",
        ],
        "steps": [
            "Chop cucumber, tomatoes, and red onion.",
            "Combine in a large bowl with olives.",
            "Crumble feta on top.",
            "Dress with olive oil, vinegar, and oregano.",
            "Toss gently and serve.",
        ],
        "tags": ["greek", "salad", "vegetarian"],
        "prep_time": 15,
        "cook_time": 0,
        "servings": 4,
    },
    {
        "title": "French Onion Soup",
        "ingredients": [
            "yellow onions",
            "butter",
            "beef broth",
            "white wine",
            "thyme",
            "bay leaf",
            "baguette",
            "gruyère cheese",
        ],
        "steps": [
            "Slice onions thinly and caramelize in butter for 40 min.",
            "Deglaze with white wine.",
            "Add broth, thyme, and bay leaf; simmer 20 min.",
            "Ladle into oven-safe bowls.",
            "Top with baguette slice and gruyère.",
            "Broil until cheese is bubbly and golden.",
        ],
        "tags": ["french", "soup", "comfort"],
        "prep_time": 10,
        "cook_time": 65,
        "servings": 4,
    },
    {
        "title": "Pad Thai",
        "ingredients": [
            "rice noodles",
            "shrimp",
            "tofu",
            "bean sprouts",
            "egg",
            "peanuts",
            "lime",
            "fish sauce",
            "tamarind paste",
            "sugar",
            "garlic",
            "green onion",
        ],
        "steps": [
            "Soak rice noodles in warm water 20 min.",
            "Stir-fry shrimp and tofu until golden.",
            "Push aside and scramble egg in the pan.",
            "Add drained noodles and sauce (tamarind, fish sauce, sugar).",
            "Toss with bean sprouts and green onion.",
            "Serve with crushed peanuts and lime wedge.",
        ],
        "tags": ["thai", "seafood", "noodles"],
        "prep_time": 25,
        "cook_time": 10,
        "servings": 2,
    },
    {
        "title": "Mushroom Risotto",
        "ingredients": [
            "arborio rice",
            "mixed mushrooms",
            "shallot",
            "white wine",
            "parmesan",
            "butter",
            "vegetable broth",
            "thyme",
        ],
        "steps": [
            "Sauté sliced mushrooms until golden; set aside.",
            "Cook shallot in butter, add rice, toast 2 min.",
            "Deglaze with white wine.",
            "Add warm broth one ladle at a time, stirring constantly.",
            "Fold in mushrooms, parmesan, and a knob of butter.",
            "Season and serve immediately.",
        ],
        "tags": ["italian", "vegetarian", "risotto"],
        "prep_time": 10,
        "cook_time": 35,
        "servings": 4,
    },
    {
        "title": "Banana Pancakes",
        "ingredients": [
            "ripe bananas",
            "eggs",
            "flour",
            "baking powder",
            "milk",
            "vanilla extract",
            "butter",
            "maple syrup",
        ],
        "steps": [
            "Mash bananas in a bowl.",
            "Whisk in eggs, milk, and vanilla.",
            "Fold in flour and baking powder.",
            "Cook on a buttered griddle until bubbles form, then flip.",
            "Serve stacked with maple syrup and sliced banana.",
        ],
        "tags": ["breakfast", "vegetarian", "sweet"],
        "prep_time": 10,
        "cook_time": 15,
        "servings": 2,
    },
    {
        "title": "Spaghetti Carbonara",
        "ingredients": [
            "spaghetti",
            "guanciale",
            "egg yolks",
            "pecorino romano",
            "black pepper",
        ],
        "steps": [
            "Cook spaghetti in salted water until al dente.",
            "Crisp guanciale in a pan.",
            "Whisk egg yolks with grated pecorino and pepper.",
            "Toss hot pasta with guanciale off heat.",
            "Add egg mixture and toss quickly to coat.",
            "Serve with extra pecorino and pepper.",
        ],
        "tags": ["italian", "pasta", "pork"],
        "prep_time": 5,
        "cook_time": 15,
        "servings": 2,
    },
    {
        "title": "Thai Green Curry",
        "ingredients": [
            "chicken breast",
            "coconut milk",
            "green curry paste",
            "bamboo shoots",
            "Thai basil",
            "fish sauce",
            "palm sugar",
            "eggplant",
            "lime leaves",
        ],
        "steps": [
            "Fry curry paste in coconut cream until fragrant.",
            "Add sliced chicken and cook through.",
            "Pour in remaining coconut milk.",
            "Add eggplant, bamboo shoots, and lime leaves.",
            "Season with fish sauce and palm sugar.",
            "Stir in Thai basil and serve with jasmine rice.",
        ],
        "tags": ["thai", "chicken", "curry"],
        "prep_time": 15,
        "cook_time": 20,
        "servings": 4,
    },
    {
        "title": "Caesar Salad",
        "ingredients": [
            "romaine lettuce",
            "croutons",
            "parmesan",
            "anchovy fillets",
            "garlic",
            "lemon juice",
            "olive oil",
            "Dijon mustard",
            "egg yolk",
        ],
        "steps": [
            "Blend anchovy, garlic, mustard, egg yolk, and lemon juice.",
            "Stream in olive oil to emulsify.",
            "Tear romaine into bite-sized pieces.",
            "Toss with dressing and croutons.",
            "Shave parmesan over the top.",
        ],
        "tags": ["salad", "american", "classic"],
        "prep_time": 15,
        "cook_time": 0,
        "servings": 2,
    },
    {
        "title": "Shakshuka",
        "ingredients": [
            "eggs",
            "canned tomatoes",
            "onion",
            "bell pepper",
            "garlic",
            "cumin",
            "paprika",
            "chili flakes",
            "feta",
            "cilantro",
            "olive oil",
        ],
        "steps": [
            "Sauté onion and bell pepper in olive oil.",
            "Add garlic, cumin, paprika, and chili flakes.",
            "Pour in tomatoes and simmer 10 min.",
            "Make wells and crack eggs into the sauce.",
            "Cover and cook until eggs are set.",
            "Top with crumbled feta and cilantro.",
        ],
        "tags": ["middle-eastern", "breakfast", "vegetarian"],
        "prep_time": 10,
        "cook_time": 25,
        "servings": 3,
    },
    {
        "title": "Beef Stroganoff",
        "ingredients": [
            "beef sirloin",
            "mushrooms",
            "onion",
            "sour cream",
            "beef broth",
            "flour",
            "butter",
            "Dijon mustard",
            "egg noodles",
            "parsley",
        ],
        "steps": [
            "Slice beef thinly and season.",
            "Sear beef in butter; set aside.",
            "Sauté mushrooms and onion.",
            "Sprinkle flour and stir in broth.",
            "Return beef, stir in sour cream and mustard.",
            "Serve over cooked egg noodles with parsley.",
        ],
        "tags": ["russian", "beef", "comfort"],
        "prep_time": 15,
        "cook_time": 25,
        "servings": 4,
    },
    {
        "title": "Falafel Wrap",
        "ingredients": [
            "chickpeas",
            "onion",
            "garlic",
            "cilantro",
            "parsley",
            "cumin",
            "coriander",
            "pita bread",
            "tahini",
            "lettuce",
            "tomato",
            "pickled turnip",
        ],
        "steps": [
            "Blend chickpeas, onion, garlic, herbs, and spices.",
            "Form into small patties.",
            "Deep-fry or bake at 200°C until golden.",
            "Warm pita bread.",
            "Fill with falafel, lettuce, tomato, and pickled turnip.",
            "Drizzle generously with tahini sauce.",
        ],
        "tags": ["middle-eastern", "vegetarian", "lunch"],
        "prep_time": 20,
        "cook_time": 15,
        "servings": 4,
    },
    {
        "title": "Chocolate Lava Cake",
        "ingredients": [
            "dark chocolate",
            "butter",
            "eggs",
            "sugar",
            "flour",
            "vanilla extract",
            "cocoa powder",
        ],
        "steps": [
            "Melt chocolate and butter together.",
            "Whisk eggs and sugar until thick.",
            "Fold chocolate mixture into egg mixture.",
            "Add flour and vanilla.",
            "Pour into greased ramekins.",
            "Bake at 220°C for 10-12 min (center should be jiggly).",
            "Invert onto plates and serve immediately.",
        ],
        "tags": ["dessert", "french", "chocolate"],
        "prep_time": 15,
        "cook_time": 12,
        "servings": 4,
    },
    {
        "title": "Korean Bibimbap",
        "ingredients": [
            "steamed rice",
            "ground beef",
            "spinach",
            "carrots",
            "zucchini",
            "bean sprouts",
            "egg",
            "gochujang",
            "sesame oil",
            "soy sauce",
            "garlic",
        ],
        "steps": [
            "Sauté each vegetable separately with garlic and sesame oil.",
            "Season and cook ground beef.",
            "Fry an egg sunny-side up.",
            "Arrange rice in a bowl, top with veggies, beef, and egg.",
            "Add a spoonful of gochujang.",
            "Mix everything together before eating.",
        ],
        "tags": ["korean", "beef", "rice"],
        "prep_time": 30,
        "cook_time": 20,
        "servings": 2,
    },
    {
        "title": "Caprese Bruschetta",
        "ingredients": [
            "baguette",
            "cherry tomatoes",
            "fresh mozzarella",
            "basil",
            "balsamic glaze",
            "olive oil",
            "garlic",
            "salt",
            "pepper",
        ],
        "steps": [
            "Slice baguette and toast until crisp.",
            "Rub each slice with a cut garlic clove.",
            "Dice tomatoes and mozzarella; mix with torn basil.",
            "Season with salt, pepper, and olive oil.",
            "Spoon mixture onto toasts.",
            "Drizzle with balsamic glaze.",
        ],
        "tags": ["italian", "appetizer", "vegetarian"],
        "prep_time": 15,
        "cook_time": 5,
        "servings": 6,
    },
    {
        "title": "Butter Chicken",
        "ingredients": [
            "chicken thighs",
            "yogurt",
            "garam masala",
            "turmeric",
            "butter",
            "tomato puree",
            "cream",
            "onion",
            "garlic",
            "ginger",
            "kasuri methi",
        ],
        "steps": [
            "Marinate chicken in yogurt, turmeric, and garam masala.",
            "Grill or pan-sear chicken until charred.",
            "Melt butter and sauté onion, garlic, and ginger.",
            "Add tomato puree and simmer 15 min.",
            "Stir in cream, kasuri methi, and cooked chicken.",
            "Simmer 5 min and serve with naan or rice.",
        ],
        "tags": ["indian", "chicken", "curry"],
        "prep_time": 40,
        "cook_time": 30,
        "servings": 4,
    },
    {
        "title": "Fish and Chips",
        "ingredients": [
            "cod fillets",
            "flour",
            "beer",
            "baking powder",
            "potatoes",
            "vegetable oil",
            "salt",
            "malt vinegar",
            "lemon",
            "tartar sauce",
        ],
        "steps": [
            "Cut potatoes into thick chips and par-boil 5 min.",
            "Mix flour, baking powder, salt, and beer into a batter.",
            "Heat oil to 180°C.",
            "Fry chips until golden; drain and keep warm.",
            "Dip cod in batter and fry 5-6 min until crispy.",
            "Serve with lemon, malt vinegar, and tartar sauce.",
        ],
        "tags": ["british", "seafood", "fried"],
        "prep_time": 15,
        "cook_time": 25,
        "servings": 2,
    },
]


async def _seed_admin(db, settings) -> User | None:  # noqa: ANN001
    """Create admin user if not exists."""
    result = await db.execute(select(User).where(User.email == settings.ALLOWED_EMAIL))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(
            "Admin user already exists", context={"email": settings.ALLOWED_EMAIL}
        )
        return existing

    user = await create_user(
        db,
        email=settings.ALLOWED_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=default_owner_permissions(),
        is_verified=True,
    )
    logger.info("Admin user created", context={"email": settings.ALLOWED_EMAIL})
    return user


async def _seed_recipes(db) -> None:  # noqa: ANN001
    """Insert 20 sample recipes if the table is empty."""
    count = await db.scalar(select(func.count()).select_from(Recipe))
    if count:
        logger.info("Recipes already seeded", context={"count": count})
        return

    recipes = list(SAMPLE_RECIPES)
    random.shuffle(recipes)

    for data in recipes:
        recipe = Recipe(
            title=data["title"],
            ingredients=json.dumps(data["ingredients"]),
            steps=json.dumps(data["steps"]),
            tags=json.dumps(data["tags"]),
            prep_time=data.get("prep_time"),
            cook_time=data.get("cook_time"),
            servings=data.get("servings"),
        )
        db.add(recipe)

    await db.flush()
    logger.info("Seeded sample recipes", context={"count": len(recipes)})


async def _seed_expense_categories(db) -> None:  # noqa: ANN001
    """Ensure default expense categories exist."""
    svc = ToolExpenseCategoryService(db)
    await svc.ensure_defaults()
    names = await svc.list_names()
    logger.info("Expense categories ready", context={"categories": names})


async def _seed_expenses(db) -> None:  # noqa: ANN001
    """Insert sample expenses when the table is empty."""
    count = await db.scalar(select(func.count()).select_from(ToolExpense))
    if count:
        logger.info("Expenses already seeded", context={"count": count})
        return

    for expense in build_random_expenses(25):
        db.add(expense)
    await db.flush()
    logger.info("Seeded sample expenses", context={"count": 25})


async def _seed_tasks(db, settings, owner: User | None) -> None:  # noqa: ANN001
    """Insert sample tasks for today when the table is empty."""
    count = await db.scalar(select(func.count()).select_from(Task))
    if count:
        logger.info("Tasks already seeded", context={"count": count})
        return

    telegram_user_id = settings.TELEGRAM_ALLOWED_USER_ID
    if not telegram_user_id:
        logger.warning("Skipping task seed: TELEGRAM_ALLOWED_USER_ID not set")
        return

    svc = TaskService(db)
    actor_id = owner.id if owner else None
    for task in build_tasks_for_today(
        25,
        telegram_user_id=telegram_user_id,
        timezone=settings.TIMEZONE,
    ):
        await svc.create_task(
            telegram_user_id=task.telegram_user_id,
            title=task.title,
            scheduled_at=task.scheduled_at,
            description=task.description,
            location=task.location,
            source=AuditSource.WEB_ADMIN,
            actor_type=AuditActorType.USER,
            actor_id=actor_id,
        )
    logger.info("Seeded sample tasks", context={"count": 25})


async def seed() -> None:
    settings = get_settings()
    if not settings.SEED_PASSWORD or settings.SEED_PASSWORD.lower() in WEAK_PASSWORDS:
        raise RuntimeError("SEED_PASSWORD env var missing or too weak")

    async with get_session_factory()() as db:
        owner = await _seed_admin(db, settings)
        await _seed_recipes(db)
        await _seed_expense_categories(db)
        await _seed_expenses(db)
        await _seed_tasks(db, settings, owner)
        await db.commit()
