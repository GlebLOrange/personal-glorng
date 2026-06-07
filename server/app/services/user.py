"""User creation and lookup helpers."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import SUPERUSER_PERMISSION, validate_permissions
from app.core.security import hash_password
from app.db.models.user import User


async def get_user_by_public_id(
    db: AsyncSession,
    public_id: str | uuid.UUID,
) -> User | None:
    """Load a user by public UUID."""
    try:
        if isinstance(public_id, uuid.UUID):
            uid = public_id
        else:
            uid = uuid.UUID(str(public_id))
    except ValueError:
        return None
    result = await db.execute(select(User).where(User.public_id == uid))
    return result.scalar_one_or_none()


def default_user_permissions() -> list[str]:
    """No tool access until a superuser grants capabilities."""
    return []


def default_display_name(email: str) -> str:
    """Derive a friendly label from the email local-part."""
    return email.split("@", maxsplit=1)[0]


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    password: str,
    permissions: list[str] | None = None,
    is_verified: bool = False,
    display_name: str | None = None,
    timezone: str = "UTC",
    preferences: dict[str, object] | None = None,
) -> User:
    """Create a user with hashed password and validated permissions."""
    perms = validate_permissions(permissions or [])
    user = User(
        email=email.strip().lower(),
        hashed_password=hash_password(password),
        is_verified=is_verified,
        permissions=perms,
        display_name=display_name or default_display_name(email),
        timezone=timezone,
        preferences=preferences or {},
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


def default_owner_permissions() -> list[str]:
    """Full platform access for the sole owner account."""
    return [SUPERUSER_PERMISSION]
