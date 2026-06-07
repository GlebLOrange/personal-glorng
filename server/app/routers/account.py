from fastapi import APIRouter, Response

from app.core.deps import CurrentUser, JobQueueDep
from app.core.logging import logger
from app.db.deps import DbRegistry
from app.schemas.auth import (
    ChangeEmailRequest,
    ChangePasswordRequest,
    DeleteAccountRequest,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserPreferencesResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.account import (
    change_email,
    change_password,
    delete_account,
    get_preferences,
    update_preferences,
    update_profile,
)
from app.workers.job_names import JobName

router = APIRouter()


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Update profile",
    description="Update display name and timezone for the authenticated user.",
)
async def patch_me(
    data: UpdateProfileRequest,
    user: CurrentUser,
    registry: DbRegistry,
) -> UserResponse:
    updated = await update_profile(
        registry,
        user,
        display_name=data.display_name,
        timezone=data.timezone,
    )
    return UserResponse.model_validate(updated)


@router.patch(
    "/me/email",
    response_model=MessageResponse,
    summary="Change email",
    description="Change email address and send a new verification link.",
)
async def patch_email(
    data: ChangeEmailRequest,
    user: CurrentUser,
    registry: DbRegistry,
    job_queue: JobQueueDep,
) -> MessageResponse:
    updated, token = await change_email(
        registry,
        user,
        new_email=str(data.email),
        current_password=data.current_password,
    )
    await job_queue.enqueue(JobName.SEND_VERIFICATION_EMAIL, updated.email, token)
    logger.info(
        "Verification email queued after email change",
        context={"user_id": user.id},
    )
    return MessageResponse(
        message="Email updated. Check your inbox to verify the new address.",
    )


@router.post(
    "/change-password",
    response_model=MessageResponse,
    summary="Change password",
    description="Change password for the authenticated user.",
)
async def post_change_password(
    data: ChangePasswordRequest,
    user: CurrentUser,
    registry: DbRegistry,
) -> MessageResponse:
    await change_password(
        registry,
        user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    return MessageResponse(message="Password changed successfully")


@router.get(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Get preferences",
)
async def get_me_preferences(user: CurrentUser) -> UserPreferencesResponse:
    prefs = get_preferences(user)
    return UserPreferencesResponse(
        display_currency=prefs.get("display_currency"),  # type: ignore[arg-type]
    )


@router.patch(
    "/me/preferences",
    response_model=UserPreferencesResponse,
    summary="Update preferences",
)
async def patch_me_preferences(
    data: UpdatePreferencesRequest,
    user: CurrentUser,
    registry: DbRegistry,
) -> UserPreferencesResponse:
    updates = data.model_dump(exclude_unset=True)
    prefs = await update_preferences(registry, user, updates)
    return UserPreferencesResponse(
        display_currency=prefs.get("display_currency"),  # type: ignore[arg-type]
    )


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Delete account",
    description="Permanently delete the authenticated user's account.",
)
async def delete_me(
    data: DeleteAccountRequest,
    user: CurrentUser,
    registry: DbRegistry,
    response: Response,
) -> MessageResponse:
    await delete_account(registry, user, current_password=data.current_password)
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
    return MessageResponse(message="Account deleted successfully")
