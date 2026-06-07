from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.mongodb import get_mongodb_client, is_mongodb_enabled
from app.core.redis import get_redis_client
from app.settings import Settings, get_settings

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Health check",
    description="Liveness probe; confirms the API process is running.",
)
async def health() -> dict[str, str]:
    return {"status": "ok"}


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
    checks: dict[str, str] = {}

    if settings.enable_mongodb() and is_mongodb_enabled():
        try:
            await get_mongodb_client().admin.command("ping")
            checks["mongodb"] = "ok"
        except Exception:
            checks["mongodb"] = "error"
    elif settings.enable_mongodb():
        checks["mongodb"] = "error"

    try:
        pong = await get_redis_client().ping()
        checks["redis"] = "ok" if pong else "error"
    except Exception:
        checks["redis"] = "error"

    if settings.enable_postgres():
        registry = getattr(request.app.state, "db_registry", None)
        if registry is not None and registry.has_postgres():
            try:
                factory = registry.require_postgres_factory()
                async with factory() as session:
                    await session.execute(text("SELECT 1"))
                checks["postgres"] = "ok"
            except Exception:
                checks["postgres"] = "error"
        else:
            checks["postgres"] = "error"

    all_ok = all(value == "ok" for value in checks.values())
    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
