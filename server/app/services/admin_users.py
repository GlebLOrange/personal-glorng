"""Superuser user management."""

import uuid

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import logger
from app.core.permissions import SUPERUSER_PERMISSION, validate_permissions
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.services.user import ensure_user_mutable, get_user_by_public_id


async def list_users(registry: DatabaseRegistry) -> list[User]:
    return await registry.users.list_all()  # type: ignore[union-attr]


async def get_user_detail(registry: DatabaseRegistry, public_id: uuid.UUID) -> User:
    user = await get_user_by_public_id(registry, public_id)
    if not user:
        raise NotFoundError("User not found")
    return user


async def update_user_permissions(
    registry: DatabaseRegistry,
    public_id: uuid.UUID,
    permissions: list[str],
) -> User:
    user = await get_user_detail(registry, public_id)
    ensure_user_mutable(user)
    validated = validate_permissions(permissions)

    had_superuser = SUPERUSER_PERMISSION in (user.permissions or [])
    will_have_superuser = SUPERUSER_PERMISSION in validated

    if had_superuser and not will_have_superuser:
        superuser_count = await registry.users.count_superusers(SUPERUSER_PERMISSION)  # type: ignore[union-attr]
        if superuser_count <= 1:
            raise ConflictError("Cannot remove superuser from the last admin account")

    user = await registry.users.update_fields(user.id, permissions=validated)  # type: ignore[union-attr]

    logger.info(
        "User permissions updated",
        context={"user_id": user.id, "permissions": validated},
    )
    return user
