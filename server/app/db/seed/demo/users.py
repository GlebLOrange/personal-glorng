"""Demo user seeding."""

from app.core.logging import logger
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import (
    DEMO_READER_EMAIL,
    DEMO_WRITER_EMAIL,
    demo_reader_permissions,
    demo_writer_permissions,
)
from app.db.seed.core.admin import seed_admin
from app.services.user import create_user, get_user_by_email
from app.settings import Settings


async def ensure_demo_user(
    registry: DatabaseRegistry,
    *,
    email: str,
    password: str,
    permissions: list[str],
) -> User:
    """Create a demo user when missing."""
    existing = await get_user_by_email(registry, email)
    if existing:
        logger.info("Demo user already exists", context={"email": email})
        return existing
    user = await create_user(
        registry,
        email=email,
        password=password,
        permissions=permissions,
        is_verified=True,
        is_protected=False,
    )
    logger.info("Demo user created", context={"email": email})
    return user


async def seed_demo_users(
    registry: DatabaseRegistry,
    settings: Settings,
) -> tuple[User, User, User]:
    """Ensure admin plus two capability-based demo users."""
    admin = await seed_admin(registry, settings)
    if admin is None:
        msg = "Failed to seed admin user"
        raise RuntimeError(msg)
    reader = await ensure_demo_user(
        registry,
        email=DEMO_READER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_reader_permissions(),
    )
    writer = await ensure_demo_user(
        registry,
        email=DEMO_WRITER_EMAIL,
        password=settings.SEED_PASSWORD,
        permissions=demo_writer_permissions(),
    )
    return admin, reader, writer
