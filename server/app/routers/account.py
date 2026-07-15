from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.core.deps import CurrentUser, JobQueueDep, oauth2_scheme
from app.core.logging import logger
from app.core.rate_limit import rate_limit_auth
from app.core.redis import blacklist_token
from app.core.security import decode_token
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

_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"


async def _blacklist_request_tokens(
    *,
    bearer_token: str | None,
    request: Request,
) -> None:
    """Revoke the access/refresh tokens presented with this request."""
    for raw_token in [
        bearer_token,
        request.cookies.get(_ACCESS_COOKIE),
        request.cookies.get(_REFRESH_COOKIE),
    ]:
        if not raw_token:
            continue
        try:
            payload = decode_token(raw_token)
            jti = payload.get("jti", "")
            exp = payload.get("exp", 0)
            now = int(datetime.now(UTC).timestamp())
            await blacklist_token(jti, max(exp - now, 0))
        except ValueError:
            pass


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE, path="/")
    response.delete_cookie(_REFRESH_COOKIE, path="/")


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
    dependencies=[Depends(rate_limit_auth)],
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
    description=(
        "Change password for the authenticated user. "
        "Existing session tokens are revoked; the client must log in again."
    ),
    dependencies=[Depends(rate_limit_auth)],
)
async def post_change_password(
    data: ChangePasswordRequest,
    user: CurrentUser,
    registry: DbRegistry,
    request: Request,
    response: Response,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> MessageResponse:
    await change_password(
        registry,
        user,
        current_password=data.current_password,
        new_password=data.new_password,
    )
    await _blacklist_request_tokens(bearer_token=token, request=request)
    _clear_auth_cookies(response)
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
    dependencies=[Depends(rate_limit_auth)],
)
async def delete_me(
    data: DeleteAccountRequest,
    user: CurrentUser,
    registry: DbRegistry,
    response: Response,
) -> MessageResponse:
    await delete_account(registry, user, current_password=data.current_password)
    _clear_auth_cookies(response)
    return MessageResponse(message="Account deleted successfully")
