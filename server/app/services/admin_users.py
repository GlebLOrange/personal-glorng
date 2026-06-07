"""Superuser user management."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import logger
from app.core.permissions import SUPERUSER_PERMISSION, validate_permissions
from app.db.models.user import User
from app.services.user import get_user_by_public_id


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at.asc()))
    return list(result.scalars().all())


async def get_user_detail(db: AsyncSession, public_id: uuid.UUID) -> User:
    user = await get_user_by_public_id(db, public_id)
    if not user:
        raise NotFoundError("User not found")
    return user


async def _count_superusers(db: AsyncSession) -> int:
    result = await db.execute(select(User))
    return sum(
        1
        for user in result.scalars().all()
        if SUPERUSER_PERMISSION in (user.permissions or [])
    )


async def update_user_permissions(
    db: AsyncSession,
    public_id: uuid.UUID,
    permissions: list[str],
) -> User:
    user = await get_user_detail(db, public_id)
    validated = validate_permissions(permissions)

    had_superuser = SUPERUSER_PERMISSION in (user.permissions or [])
    will_have_superuser = SUPERUSER_PERMISSION in validated

    if had_superuser and not will_have_superuser:
        superuser_count = await _count_superusers(db)
        if superuser_count <= 1:
            raise ConflictError("Cannot remove superuser from the last admin account")

    user.permissions = validated
    await db.flush()
    await db.refresh(user)

    logger.info(
        "User permissions updated",
        context={"user_id": user.id, "permissions": validated},
    )
    return user
