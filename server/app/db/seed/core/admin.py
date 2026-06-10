"""Admin user seeding for core and demo flows."""

from app.core.logging import logger
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.user import create_user, default_owner_permissions, get_user_by_email
from app.settings import Settings

WEAK_PASSWORDS = {"changeme", "password", "admin", "123456", "secret"}


def require_repos(registry: DatabaseRegistry) -> None:
    """Ensure required repositories are initialized."""
    if registry.users is None or registry.recipes is None or registry.expenses is None:
        msg = "Database repositories are not initialized"
        raise RuntimeError(msg)


async def seed_admin(registry: DatabaseRegistry, settings: Settings) -> User | None:
    """Create admin user if not exists."""
    require_repos(registry)
    existing = await get_user_by_email(registry, settings.ALLOWED_EMAIL)
    if existing:
        if not existing.is_protected:
            await registry.users.update_fields(existing.id, is_protected=True)
        logger.info(
            "Admin user already exists", context={"email": settings.ALLOWED_EMAIL}
        )
        return existing

    user = await create_user(
        registry,
        email=settings.ALLOWED_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=default_owner_permissions(),
        is_verified=True,
        is_protected=True,
    )
    logger.info("Admin user created", context={"email": settings.ALLOWED_EMAIL})
    return user
