from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.redis import get_redis_client, is_token_blacklisted
from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import get_db
from app.services.ai_chat import AIProviderRegistry, build_api_keys
from app.settings import Settings, get_settings

DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

RedisClient = Annotated[Redis, Depends(get_redis_client)]


async def get_current_user(
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User:
    if not token:
        raise UnauthorizedError("Not authenticated")

    try:
        payload = decode_token(token)
    except ValueError:
        raise UnauthorizedError("Invalid token") from None

    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    jti = payload.get("jti", "")
    if await is_token_blacklisted(jti):
        raise UnauthorizedError("Token has been revoked")

    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedError("Invalid token payload")

    try:
        uid = int(user_id)
    except (ValueError, TypeError):
        raise UnauthorizedError("Invalid token payload") from None

    result = await db.execute(select(User).where(User.id == uid))
    user = result.scalar_one_or_none()

    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_verified:
        raise ForbiddenError("Email not verified")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def require_admin(user: CurrentUser) -> User:
    if not user.is_admin:
        raise ForbiddenError("Admin access required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]


def get_ai_registry(settings: AppSettings) -> AIProviderRegistry:
    return AIProviderRegistry(api_keys=build_api_keys(settings))


AIRegistry = Annotated[AIProviderRegistry, Depends(get_ai_registry)]
