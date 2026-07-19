"""Superuser user management."""

import asyncio
import uuid
from typing import Literal

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logging import logger
from app.core.pagination import build_paginated
from app.core.permissions import SUPERUSER_PERMISSION, validate_permissions
from app.core.utils import DEFAULT_PER_PAGE, paginate_params
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.schemas.admin_users import (
    AdminUserListResponse,
    AdminUsersStatsResponse,
    AdminUserSummary,
)
from app.services.user import ensure_user_mutable, get_user_by_public_id

RoleQuery = Literal["all", "superuser", "custom"]
StatusQuery = Literal["all", "verified", "unverified", "protected"]


async def list_users(registry: DatabaseRegistry) -> list[User]:
    return await registry.users.list_all()  # type: ignore[union-attr]


async def list_users_paginated(
    registry: DatabaseRegistry,
    *,
    page: int = 1,
    per_page: int = DEFAULT_PER_PAGE,
    search: str | None = None,
    role: RoleQuery = "all",
    status: StatusQuery = "all",
) -> AdminUserListResponse:
    offset, limit = paginate_params(page, per_page)
    users, total = await asyncio.gather(
        registry.users.list_admin(  # type: ignore[union-attr]
            offset=offset,
            limit=limit,
            search=search,
            role=role,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
        ),
        registry.users.count_admin(  # type: ignore[union-attr]
            search=search,
            role=role,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
        ),
    )
    items = [AdminUserSummary.model_validate(user) for user in users]
    safe_page = max(1, page)
    return build_paginated(
        items,
        total=total,
        page=safe_page,
        per_page=limit,
    )


async def get_users_stats(registry: DatabaseRegistry) -> AdminUsersStatsResponse:
    stats = await registry.users.admin_stats()  # type: ignore[union-attr]
    return AdminUsersStatsResponse.model_validate(stats)


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
