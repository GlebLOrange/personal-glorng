import asyncio
from typing import Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text

from app.core.mongodb import get_mongodb_client, is_mongodb_enabled
from app.core.redis import get_redis_client, get_redis_memory_info
from app.settings import Settings, get_settings
from app.workers.broker_health import check_broker_connection

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check",
    description="Liveness probe; confirms the API process is running.",
)
async def health() -> dict[str, str]:
    return {"status": "ok"}


async def _check_mongodb(settings: Settings) -> str:
    if settings.enable_mongodb() and is_mongodb_enabled():
        try:
            await get_mongodb_client().admin.command("ping")
            return "ok"
        except Exception:
            return "error"
    if settings.enable_mongodb():
        return "error"
    return "skipped"


async def _check_redis() -> tuple[str, dict[str, Any] | None]:
    try:
        pong = await get_redis_client().ping()
        if not pong:
            return "error", None
        memory = await get_redis_memory_info()
        status_value = "warn" if memory.get("warning") else "ok"
        return status_value, memory
    except RedisError:
        return "error", None


async def _check_broker(settings: Settings) -> str | None:
    if not settings.CELERY_BROKER_URL:
        return None
    broker_ok = await asyncio.to_thread(check_broker_connection)
    return "ok" if broker_ok else "degraded"


async def _check_postgres(request: Request, settings: Settings) -> str | None:
    if not settings.enable_postgres():
        return None
    registry = getattr(request.app.state, "db_registry", None)
    if registry is not None and registry.has_postgres():
        try:
            factory = registry.require_postgres_factory()
            async with factory() as session:
                await session.execute(text("SELECT 1"))
            return "ok"
        except Exception:
            return "error"
    return "error"


@router.get(
    "/ready",
    summary="Readiness check",
    description=(
        "Readiness probe; verifies MongoDB (primary), Redis, and optional Postgres."
    ),
)
async def ready(
    request: Request,
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    mongo_status, (redis_status, redis_memory), broker_status, postgres_status = (
        await asyncio.gather(
            _check_mongodb(settings),
            _check_redis(),
            _check_broker(settings),
            _check_postgres(request, settings),
        )
    )

    checks: dict[str, Any] = {}
    if mongo_status != "skipped":
        checks["mongodb"] = mongo_status
    checks["redis"] = redis_status
    if redis_memory is not None:
        checks["redis_memory"] = redis_memory
    if broker_status is not None:
        checks["rabbitmq"] = broker_status
    if postgres_status is not None:
        checks["postgres"] = postgres_status

    critical_checks = {
        key: value
        for key, value in checks.items()
        if key in {"mongodb", "redis", "postgres"}
    }
    all_ok = all(value in {"ok", "warn"} for value in critical_checks.values())
    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
