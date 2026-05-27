from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, UnauthorizedError
from app.core.logging import logger
from app.core.redis import blacklist_token, is_token_blacklisted
from app.core.security import (
    create_access_token,
    create_refresh_token,
    create_reset_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.settings import get_settings


async def _decode_and_validate(token: str, expected_type: str) -> dict[str, object]:
    """Decode a JWT and verify its type claim, raising UnauthorizedError on failure."""
    try:
        payload = decode_token(token)
    except ValueError:
        raise UnauthorizedError(
            f"Invalid or expired {expected_type} token",
        ) from None

    if payload.get("type") != expected_type:
        raise UnauthorizedError("Invalid token type")

    if not payload.get("sub"):
        raise UnauthorizedError("Invalid token payload")

    jti = payload.get("jti")
    if jti and await is_token_blacklisted(jti):
        raise UnauthorizedError("Token has already been used")

    return payload


async def _blacklist_payload(payload: dict[str, object]) -> None:
    """Blacklist a token's JTI for its remaining lifetime."""
    jti = payload.get("jti")
    if not jti:
        return
    exp = payload.get("exp", 0)
    now = int(datetime.now(UTC).timestamp())
    await blacklist_token(jti, max(exp - now, 0))


async def _get_user_by_id(db: AsyncSession, user_id: str) -> User:
    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid token payload") from None
    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")
    return user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, email: str, password: str) -> User:
    settings = get_settings()

    if email != settings.ALLOWED_EMAIL:
        logger.warning("Registration denied", context={"email": email})
        raise ForbiddenError("Registration is restricted to authorized emails only")

    existing = await get_user_by_email(db, email)
    if existing:
        raise ConflictError("User with this email already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        is_verified=False,
        is_admin=True,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    return user


async def login_user(db: AsyncSession, email: str, password: str) -> tuple[str, str]:
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Login failed", context={"email": email})
        raise UnauthorizedError("Invalid email or password")

    if not user.is_verified:
        raise ForbiddenError("Email not verified. Check your inbox.")

    logger.info("Login successful", context={"user_id": user.id})
    access_token = create_access_token(str(user.id))
    refresh_token = create_refresh_token(str(user.id))
    return access_token, refresh_token


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> tuple[str, str]:
    payload = await _decode_and_validate(refresh_token, "refresh")
    await _blacklist_payload(payload)
    user = await _get_user_by_id(db, payload["sub"])
    new_access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    return new_access, new_refresh


async def verify_user_email(db: AsyncSession, token: str) -> User:
    payload = await _decode_and_validate(token, "verify")
    user = await get_user_by_email(db, payload["sub"])
    if not user:
        raise UnauthorizedError("User not found")

    user.is_verified = True
    await db.flush()
    await db.refresh(user)

    await _blacklist_payload(payload)

    return user


async def request_password_reset(db: AsyncSession, email: str) -> str | None:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    return create_reset_token(email)


async def reset_user_password(db: AsyncSession, token: str, new_password: str) -> User:
    payload = await _decode_and_validate(token, "reset")
    user = await get_user_by_email(db, payload["sub"])
    if not user:
        raise UnauthorizedError("User not found")

    user.hashed_password = hash_password(new_password)
    await db.flush()
    await db.refresh(user)

    await _blacklist_payload(payload)
    logger.info("Password reset completed", context={"user_id": user.id})

    return user
