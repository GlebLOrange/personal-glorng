from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response

from app.core.deps import AppSettings, CurrentUser, DbSession, oauth2_scheme
from app.core.exceptions import UnauthorizedError
from app.core.logging import logger
from app.core.rate_limit import rate_limit_auth
from app.core.redis import blacklist_token
from app.core.security import create_verification_token, decode_token
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserResponse,
)
from app.schemas.common import MessageResponse
from app.services.auth import (
    login_user,
    record_logout,
    refresh_access_token,
    register_user,
    request_password_reset,
    reset_user_password,
    verify_user_email,
)
from app.services.user import get_user_by_public_id
from app.settings import Settings
from app.workers.pool import enqueue_job

router = APIRouter()

_ACCESS_COOKIE = "access_token"
_REFRESH_COOKIE = "refresh_token"


def _cookie_flags(settings: Settings) -> dict[str, object]:
    secure = settings.APP_ENV == "production"
    return {
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
        "path": "/",
    }


def _set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
    settings: Settings,
) -> None:
    access_max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    refresh_max_age = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    flags = _cookie_flags(settings)

    response.set_cookie(
        _ACCESS_COOKIE,
        access_token,
        max_age=access_max_age,
        **flags,
    )
    response.set_cookie(
        _REFRESH_COOKIE,
        refresh_token,
        max_age=refresh_max_age,
        **flags,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(_ACCESS_COOKIE, path="/")
    response.delete_cookie(_REFRESH_COOKIE, path="/")


@router.post(
    "/register",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def register(data: RegisterRequest, db: DbSession) -> MessageResponse:
    user = await register_user(db, data.email, data.password)
    _token = create_verification_token(user.email)

    logger.info("User registered", context={"email": user.email})
    await enqueue_job("send_verification_email", user.email, _token)
    return MessageResponse(
        message="Registration successful. Check your email to verify your account."
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def login(
    data: LoginRequest,
    db: DbSession,
    response: Response,
    settings: AppSettings,
) -> TokenResponse:
    access_token, refresh_token = await login_user(db, data.email, data.password)
    _set_auth_cookies(
        response,
        access_token=access_token,
        refresh_token=refresh_token,
        settings=settings,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get(
    "/verify",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def verify(token: str, db: DbSession) -> MessageResponse:
    await verify_user_email(db, token)
    return MessageResponse(message="Email verified successfully")


@router.post(
    "/refresh",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def refresh(
    db: DbSession,
    response: Response,
    request: Request,
    settings: AppSettings,
    data: RefreshRequest | None = None,
) -> TokenResponse:
    refresh_token = (data.refresh_token if data else None) or request.cookies.get(
        _REFRESH_COOKIE
    )
    if not refresh_token:
        raise UnauthorizedError("Missing refresh token")

    access_token, new_refresh_token = await refresh_access_token(db, refresh_token)
    _set_auth_cookies(
        response,
        access_token=access_token,
        refresh_token=new_refresh_token,
        settings=settings,
    )
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def logout(
    db: DbSession,
    response: Response,
    request: Request,
    data: LogoutRequest | None = None,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> MessageResponse:
    user_id: int | None = None
    _clear_auth_cookies(response)

    for raw_token in [
        token,
        data.refresh_token if data else None,
        request.cookies.get(_ACCESS_COOKIE),
        request.cookies.get(_REFRESH_COOKIE),
    ]:
        if not raw_token:
            continue
        try:
            payload = decode_token(raw_token)
            sub = payload.get("sub")
            if sub and user_id is None:
                user = await get_user_by_public_id(db, str(sub))
                if user:
                    user_id = user.id
            jti = payload.get("jti", "")
            exp = payload.get("exp", 0)
            now = int(datetime.now(UTC).timestamp())
            ttl = max(exp - now, 0)
            await blacklist_token(jti, ttl)
        except ValueError:
            pass

    await record_logout(db, user_id)

    return MessageResponse(message="Logged out successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def forgot_password(
    data: ForgotPasswordRequest, db: DbSession
) -> MessageResponse:
    token = await request_password_reset(db, data.email)
    if token:
        logger.info(
            "Password reset requested",
            context={"email": data.email},
        )
        await enqueue_job("send_reset_email", data.email, token)
    return MessageResponse(
        message="If the email exists, a reset link has been sent",
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def reset_password(data: ResetPasswordRequest, db: DbSession) -> MessageResponse:
    await reset_user_password(db, data.token, data.new_password)
    return MessageResponse(message="Password reset successfully")


@router.get("/me", response_model=UserResponse)
async def me(user: CurrentUser) -> UserResponse:
    return UserResponse.model_validate(user)
