from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.deps import CurrentUser, DbSession, oauth2_scheme
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
    refresh_access_token,
    register_user,
    request_password_reset,
    reset_user_password,
    verify_user_email,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def register(data: RegisterRequest, db: DbSession) -> MessageResponse:
    user = await register_user(db, data.email, data.password)
    _token = create_verification_token(user.email)
    logger.info("User registered", context={"email": user.email})
    # TODO: enqueue email via ARQ
    # await arq_pool.enqueue_job(
    #     "send_verification_email", user.email, _token,
    # )
    return MessageResponse(
        message="Registration successful. Check your email to verify your account."
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def login(data: LoginRequest, db: DbSession) -> TokenResponse:
    access_token, refresh_token = await login_user(db, data.email, data.password)
    logger.info("User logged in", context={"email": data.email})
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
async def refresh(data: RefreshRequest, db: DbSession) -> TokenResponse:
    access_token, refresh_token = await refresh_access_token(db, data.refresh_token)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit_auth)],
)
async def logout(
    data: LogoutRequest | None = None,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> MessageResponse:
    for raw_token in [token, data.refresh_token if data else None]:
        if not raw_token:
            continue
        try:
            payload = decode_token(raw_token)
            jti = payload.get("jti", "")
            exp = payload.get("exp", 0)
            now = int(datetime.now(UTC).timestamp())
            ttl = max(exp - now, 0)
            await blacklist_token(jti, ttl)
        except ValueError:
            pass
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
        # TODO: enqueue via ARQ
        # await arq_pool.enqueue_job(
        #     "send_reset_email", data.email, token,
        # )
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
