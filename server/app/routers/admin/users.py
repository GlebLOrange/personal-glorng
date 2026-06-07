import uuid

from fastapi import APIRouter

from app.core.deps import AdminUser
from app.db.deps import DbRegistry
from app.schemas.admin_users import AdminUserSummary, UpdateUserPermissionsRequest
from app.services.admin_users import (
    get_user_detail,
    list_users,
    update_user_permissions,
)

router = APIRouter()


@router.get(
    "",
    response_model=list[AdminUserSummary],
    summary="List users",
)
async def get_users(_admin: AdminUser, registry: DbRegistry) -> list[AdminUserSummary]:
    users = await list_users(registry)
    return [AdminUserSummary.model_validate(user) for user in users]


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
