"""User creation and lookup helpers."""

import uuid

from app.core.exceptions import ConflictError
from app.core.permissions import SUPERUSER_PERMISSION, validate_permissions
from app.core.security import hash_password
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry


def _users(registry: DatabaseRegistry):
    if registry.users is None:
        msg = "Users repository is not initialized"
        raise RuntimeError(msg)
    return registry.users


async def get_user_by_public_id(
    registry: DatabaseRegistry,
    public_id: str | uuid.UUID,
) -> User | None:
    """Load a user by public UUID."""
    return await _users(registry).get_by_public_id(public_id)


def default_user_permissions() -> list[str]:
    """No tool access until a superuser grants capabilities."""
    return []


def default_display_name(email: str) -> str:
    """Derive a friendly label from the email local-part."""
    return email.split("@", maxsplit=1)[0]


def ensure_user_mutable(user: User) -> None:
    """Raise when a protected account must not be modified.

    Scope is intentional and narrow: blocks account deletion and admin
    permission changes only. Self-service profile, email, password, and
    preferences updates remain allowed so the seeded owner can use Settings.
    """
    if user.is_protected:
        raise ConflictError("This account is protected and cannot be modified")


async def get_user_by_email(registry: DatabaseRegistry, email: str) -> User | None:
    return await _users(registry).get_by_email(email)


async def create_user(
    registry: DatabaseRegistry,
    *,
    email: str,
    password: str,
    permissions: list[str] | None = None,
    is_verified: bool = False,
    is_protected: bool = False,
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
        is_protected=is_protected,
        permissions=perms,
        display_name=display_name or default_display_name(email),
        timezone=timezone,
        preferences=preferences or {},
    )
    return await _users(registry).insert(user)


def default_owner_permissions() -> list[str]:
    """Full platform access for the sole owner account."""
    return [SUPERUSER_PERMISSION]
