import uuid

from fastapi import APIRouter

from app.core.deps import AdminUser, DbSession
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
async def get_users(_admin: AdminUser, db: DbSession) -> list[AdminUserSummary]:
    users = await list_users(db)
    return [AdminUserSummary.model_validate(user) for user in users]


@router.get(
    "/{public_id}",
    response_model=AdminUserSummary,
    summary="Get user",
)
async def get_user(
    public_id: uuid.UUID,
    _admin: AdminUser,
    db: DbSession,
) -> AdminUserSummary:
    user = await get_user_detail(db, public_id)
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
    db: DbSession,
) -> AdminUserSummary:
    user = await update_user_permissions(db, public_id, data.permissions)
    return AdminUserSummary.model_validate(user)
