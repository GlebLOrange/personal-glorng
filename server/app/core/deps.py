from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.permissions import permission_key, user_has_permission
from app.core.redis import get_redis_client, is_token_blacklisted
from app.core.security import decode_token, require_matching_session_version
from app.db.deps import DbRegistry, get_postgres_db
from app.db.documents.user import User
from app.db.registry import DatabaseRegistry
from app.platform.registry import Capability, ServiceSlug
from app.services.ai_chat import GroqChatService
from app.services.audit import AuditService
from app.services.currency import CurrencyService
from app.services.expense import ExpenseService
from app.services.expense_category import ExpenseCategoryService
from app.services.news import NewsService
from app.services.recipe import RecipeService
from app.services.search_index import SearchIndexService
from app.services.task import TaskService
from app.services.task_intake import TaskIntakeService
from app.services.user import get_user_by_public_id
from app.settings import Settings, get_settings
from app.workers.queue import JobQueue, get_job_queue

AppSettings = Annotated[Settings, Depends(get_settings)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)

RedisClient = Annotated[Redis, Depends(get_redis_client)]


async def _optional_postgres_session(
    registry: DbRegistry,
    settings: AppSettings,
) -> AsyncGenerator[AsyncSession | None]:
    if not settings.enable_postgres():
        yield None
        return
    async for session in get_postgres_db(registry, settings):
        yield session


OptionalPostgresSession = Annotated[
    AsyncSession | None,
    Depends(_optional_postgres_session),
]


async def _resolve_user_from_token(
    registry: DatabaseRegistry,
    raw_token: str,
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

    user = await get_user_by_public_id(registry, str(user_sub))
    if not user:
        if strict:
            raise UnauthorizedError("User not found")
        return None

    try:
        require_matching_session_version(payload, user.session_version)
    except ValueError:
        if strict:
            raise UnauthorizedError("Token has been revoked") from None
        return None

    if not user.is_verified:
        if strict:
            raise ForbiddenError("Email not verified")
        return None

    return user


async def get_current_user(
    request: Request,
    registry: DbRegistry,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User:
    raw_token = token or request.cookies.get("access_token")
    if not raw_token:
        raise UnauthorizedError("Not authenticated")

    user = await _resolve_user_from_token(registry, raw_token, strict=True)
    return user  # strict=True raises before returning None


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_optional_current_user(
    request: Request,
    registry: DbRegistry,
    token: Annotated[str | None, Depends(oauth2_scheme)] = None,
) -> User | None:
    """Return the authenticated user when a valid session exists."""
    raw_token = token or request.cookies.get("access_token")
    if not raw_token:
        return None

    return await _resolve_user_from_token(registry, raw_token)


OptionalUser = Annotated[User | None, Depends(get_optional_current_user)]


def require_capability(
    slug: ServiceSlug,
    capability: Capability,
) -> Callable[..., object]:
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


def get_groq_chat_service(settings: AppSettings) -> GroqChatService:
    """Build Groq chat service or raise when the API key is missing."""
    if not settings.GROQ_API_KEY.strip():
        from app.core.exceptions import ApiError

        raise ApiError(503, "Groq API key is not configured")
    return GroqChatService(
        api_key=settings.GROQ_API_KEY,
        model=settings.GROQ_CHAT_MODEL,
        base_url=settings.GROQ_API_BASE_URL,
    )


GroqChatServiceDep = Annotated[GroqChatService, Depends(get_groq_chat_service)]


def get_search_index_service(
    registry: DbRegistry,
    postgres_db: OptionalPostgresSession,
) -> SearchIndexService:
    return SearchIndexService(registry, postgres_db=postgres_db)


SearchIndexServiceDep = Annotated[SearchIndexService, Depends(get_search_index_service)]


def get_job_queue_dep() -> JobQueue:
    return get_job_queue()


JobQueueDep = Annotated[JobQueue, Depends(get_job_queue_dep)]


def get_currency_service() -> CurrencyService:
    return CurrencyService()


CurrencyServiceDep = Annotated[CurrencyService, Depends(get_currency_service)]


def get_expense_category_service(registry: DbRegistry) -> ExpenseCategoryService:
    return ExpenseCategoryService(registry)


ExpenseCategoryServiceDep = Annotated[
    ExpenseCategoryService,
    Depends(get_expense_category_service),
]


def get_expense_service(
    registry: DbRegistry,
    currency_svc: CurrencyServiceDep,
) -> ExpenseService:
    return ExpenseService(registry, currency_svc=currency_svc)


ExpenseServiceDep = Annotated[ExpenseService, Depends(get_expense_service)]


def get_audit_service(
    registry: DbRegistry,
    postgres_db: OptionalPostgresSession,
) -> AuditService:
    return AuditService(registry, postgres_db=postgres_db)


AuditServiceDep = Annotated[AuditService, Depends(get_audit_service)]


def get_task_service(registry: DbRegistry) -> TaskService:
    return TaskService(registry)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]


def get_task_intake_service(registry: DbRegistry) -> TaskIntakeService:
    return TaskIntakeService(registry)


TaskIntakeServiceDep = Annotated[TaskIntakeService, Depends(get_task_intake_service)]


def get_recipe_service(
    registry: DbRegistry,
    audit_svc: AuditServiceDep,
) -> RecipeService:
    return RecipeService(registry, audit_svc)


RecipeServiceDep = Annotated[RecipeService, Depends(get_recipe_service)]


def get_news_service(
    registry: DbRegistry,
    audit_svc: AuditServiceDep,
) -> NewsService:
    return NewsService(registry, audit_svc)


NewsServiceDep = Annotated[NewsService, Depends(get_news_service)]
