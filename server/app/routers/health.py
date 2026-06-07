from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.mongodb import get_mongodb_client, is_mongodb_enabled
from app.core.redis import get_redis_client
from app.db.session import get_db
from app.settings import get_settings

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
        "Readiness probe; verifies database, Redis, and optional MongoDB connectivity."
    ),
)
async def ready(db: AsyncSession = Depends(get_db)) -> JSONResponse:
    checks: dict[str, str] = {}
    settings = get_settings()

    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    try:
        pong = await get_redis_client().ping()
        checks["redis"] = "ok" if pong else "error"
    except Exception:
        checks["redis"] = "error"

    if settings.mongodb_enabled() and is_mongodb_enabled():
        try:
            await get_mongodb_client().admin.command("ping")
            checks["mongodb"] = "ok"
        except Exception:
            checks["mongodb"] = "error"

    all_ok = all(value == "ok" for value in checks.values())
    status_code = status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={"status": "ok" if all_ok else "degraded", "checks": checks},
    )
