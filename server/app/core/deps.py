from collections.abc import Callable
from typing import Annotated

from arq import ArqRedis
from fastapi import Depends, Request
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
from app.services.audit import AuditService
from app.services.currency import CurrencyService
from app.services.recipe import RecipeService
from app.services.task import TaskService
from app.services.task_intake import TaskIntakeService
from app.services.tool_expense import ToolExpenseService
from app.services.tool_expense_category import ToolExpenseCategoryService
from app.services.user import get_user_by_public_id
from app.settings import Settings, get_settings
from app.workers.pool import get_arq_pool

DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

RedisClient = Annotated[Redis, Depends(get_redis_client)]


async def _resolve_user_from_token(
    raw_token: str,
    db: AsyncSession,
    *,
    strict: bool = False,
) -> User | None:
    try:
        payload = decode_token(raw_token)
    except ValueError:
        if strict:
            raise UnauthorizedError("Invalid token") from None
        return None

    if payload.get("type") != "access":
        if strict:
            raise UnauthorizedError("Invalid token type")
        return None

    jti = payload.get("jti", "")
    if await is_token_blacklisted(jti):
        if strict:
            raise UnauthorizedError("Token has been revoked")
        return None

    user_sub = payload.get("sub")
    if not user_sub:
        if strict:
            raise UnauthorizedError("Invalid token payload")
        return None

    user = await get_user_by_public_id(db, str(user_sub))
    if not user:
        if strict:
            raise UnauthorizedError("User not found")
        return None
    if not user.is_verified:
        if strict:
            raise ForbiddenError("Email not verified")
        return None

    return user


async def get_current_user(
    request: Request,
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User:
    raw_token = token or request.cookies.get("access_token")
    if not raw_token:
        raise UnauthorizedError("Not authenticated")

    user = await _resolve_user_from_token(raw_token, db, strict=True)
    return user  # strict=True raises before returning None


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_current_user(
    request: Request,
    db: DbSession,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User | None:
    """Return the authenticated user when a valid session exists."""
    raw_token = token or request.cookies.get("access_token")
    if not raw_token:
        return None

    return await _resolve_user_from_token(raw_token, db)


OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]


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


def get_currency_service() -> CurrencyService:
    return CurrencyService()


CurrencyServiceDep = Annotated[CurrencyService, Depends(get_currency_service)]


def get_expense_category_service(db: DbSession) -> ToolExpenseCategoryService:
    return ToolExpenseCategoryService(db)


ExpenseCategoryServiceDep = Annotated[
    ToolExpenseCategoryService,
    Depends(get_expense_category_service),
]


def get_expense_service(
    db: DbSession,
    currency_svc: CurrencyServiceDep,
) -> ToolExpenseService:
    return ToolExpenseService(db, currency_svc=currency_svc)


ExpenseServiceDep = Annotated[ToolExpenseService, Depends(get_expense_service)]


def get_audit_service(db: DbSession) -> AuditService:
    return AuditService(db)


AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


def get_task_service(db: DbSession) -> TaskService:
    return TaskService(db)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_task_intake_service(db: DbSession) -> TaskIntakeService:
    return TaskIntakeService(db)


TaskIntakeServiceDep = Annotated[TaskIntakeService, Depends(get_task_intake_service)]


def get_recipe_service(
    db: DbSession,
    audit_svc: AuditServiceDep,
) -> RecipeService:
    return RecipeService(db, audit_svc)


RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]
