from collections.abc import Callable
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ApiError, ForbiddenError, UnauthorizedError
from app.core.permissions import permission_key, user_has_permission
from app.core.redis import get_redis_client, is_token_blacklisted
from app.core.security import decode_token
from app.db.models.user import User
from app.db.session import get_db
from app.services.ai_chat import OpenAIService
from app.services.user import get_user_by_public_id
from app.settings import Settings, get_settings
from app.workers.pool import get_arq_pool

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

    user_sub = payload.get("sub")
    if not user_sub:
        raise UnauthorizedError("Invalid token payload")

    user = await get_user_by_public_id(db, str(user_sub))
    if not user:
        raise UnauthorizedError("User not found")
    if not user.is_verified:
        raise ForbiddenError("Email not verified")

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_capability(slug: str, capability: str) -> Callable[..., object]:
    """FastAPI dependency factory for a platform permission."""

    key = permission_key(slug, capability)

    async def _dep(user: CurrentUser) -> User:
        if not user_has_permission(user, key):
            raise ForbiddenError(f"Permission required: {key}")
        return user

    return _dep


AuthorizedUser = CurrentUser


async def require_admin(user: CurrentUser) -> User:
    """Backward-compatible alias: requires platform superuser."""
    if not user_has_permission(user, "platform:superuser"):
        raise ForbiddenError("Admin access required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]


def get_openai_chat_service(settings: AppSettings) -> OpenAIService:
    """Build OpenAI chat service or raise when the API key is missing."""
    if not settings.OPENAI_API_KEY:
        raise ApiError(503, "OpenAI API key is not configured")
    return OpenAIService(
        api_key=settings.OPENAI_API_KEY,
        model=settings.OPENAI_CHAT_MODEL,
    )


OpenAIChatService = Annotated[OpenAIService, Depends(get_openai_chat_service)]


def get_arq_pool_dep() -> ArqRedis:
    return get_arq_pool()


ArqPool = Annotated[ArqRedis, Depends(get_arq_pool_dep)]
