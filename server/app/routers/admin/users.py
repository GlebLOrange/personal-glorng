import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query

from app.core.deps import AdminUser
from app.core.rate_limit import rate_limit_admin
from app.core.utils import DEFAULT_PER_PAGE
from app.db.deps import DbRegistry
from app.schemas.admin_users import (
    AdminUserListResponse,
    AdminUsersStatsResponse,
    AdminUserSummary,
    UpdateUserPermissionsRequest,
)
from app.services.admin_users import (
    get_user_detail,
    get_users_stats,
    list_users_paginated,
    update_user_permissions,
)

router = APIRouter(dependencies=[Depends(rate_limit_admin)])

RoleQuery = Literal["all", "superuser", "custom"]
StatusQuery = Literal["all", "verified", "unverified", "protected"]


@router.get(
    "",
    response_model=AdminUserListResponse,
    summary="List users",
)
async def get_users(
    _admin: AdminUser,
    registry: DbRegistry,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = DEFAULT_PER_PAGE,
    search: Annotated[str | None, Query(max_length=120)] = None,
    role: RoleQuery = "all",
    status: StatusQuery = "all",
) -> AdminUserListResponse:
    return await list_users_paginated(
        registry,
        page=page,
        per_page=per_page,
        search=search,
        role=role,
        status=status,
    )


@router.get(
    "/stats",
    response_model=AdminUsersStatsResponse,
    summary="Get user summary stats",
)
async def get_user_stats(
    _admin: AdminUser,
    registry: DbRegistry,
) -> AdminUsersStatsResponse:
    return await get_users_stats(registry)


@router.get(
    "/{public_id}",
    response_model=AdminUserSummary,
    summary="Get user",
)
async def get_user(
    public_id: uuid.UUID,
    _admin: AdminUser,
    registry: DbRegistry,
) -> AdminUserSummary:
    user = await get_user_detail(registry, public_id)
    return AdminUserSummary.model_validate(user)


@router.patch(
    "/{public_id}/permissions",
    response_model=AdminUserSummary,
    summary="Update user permissions",
)
async def patch_permissions(
    public_id: uuid.UUID,
    data: UpdateUserPermissionsRequest,
    _admin: AdminUser,
    registry: DbRegistry,
) -> AdminUserSummary:
    user = await update_user_permissions(registry, public_id, data.permissions)
    return AdminUserSummary.model_validate(user)
