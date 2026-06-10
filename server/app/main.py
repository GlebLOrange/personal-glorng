from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.app_log_persist import start_app_log_worker, stop_app_log_worker
from app.core.elasticsearch import (
    close_elasticsearch,
    init_elasticsearch,
    is_elasticsearch_enabled,
)
from app.core.exceptions import ApiError
from app.core.logging import logger
from app.core.mongodb import bind_mongodb, clear_mongodb
from app.core.redis import close_redis, init_redis
from app.db.init_service import DatabaseInitService
from app.db.registry import DatabaseRegistry
from app.openapi import configure_openapi
from app.services.elasticsearch_search import ensure_index
from app.services.search_bootstrap import bootstrap_resume_index
from app.settings import get_settings
from app.workers.queue import close_job_queue, init_job_queue


def _init_sentry() -> None:
    """Initialize Sentry before the FastAPI app is created."""
    settings = get_settings()
    if not settings.sentry_enabled():
        return

    sentry_sdk.init(
        dsn=settings.SERVER_SENTRY_DSN,
        environment=settings.APP_ENV,
        release=settings.SERVER_SENTRY_RELEASE or None,
        send_default_pii=False,
        traces_sample_rate=0.2,
        profile_session_sample_rate=0.2 if settings.APP_ENV == "production" else 0.0,
        profile_lifecycle="trace",
        enable_logs=True,
    )
    logger.info("Sentry initialized", context={"env": settings.APP_ENV})


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    settings = get_settings()

    await init_redis(settings.REDIS_URL)
    logger.info("Redis connected")

    if settings.elasticsearch_enabled():
        await init_elasticsearch(settings.ELASTICSEARCH_URL)
        if is_elasticsearch_enabled():
            await ensure_index()

    registry = DatabaseRegistry()
    init_svc = DatabaseInitService(registry, settings)
    await init_svc.startup()
    _app.state.db_registry = registry
    if registry.mongo_client is not None and registry.mongo_db is not None:
        bind_mongodb(registry.mongo_client, registry.mongo_db)
        await start_app_log_worker()

    init_job_queue()

    if registry.mongo_db is not None and registry.search is not None:
        await bootstrap_resume_index(registry)

    yield

    await close_job_queue()
    await stop_app_log_worker()
    await init_svc.shutdown()
    clear_mongodb()
    await close_elasticsearch()
    await close_redis()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    _init_sentry()
    settings = get_settings()

    is_dev = settings.APP_ENV == "development"
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/api/docs" if is_dev else None,
        redoc_url="/api/redoc" if is_dev else None,
        openapi_url="/api/openapi.json" if is_dev else None,
        lifespan=lifespan,
    )

    @application.exception_handler(ApiError)
    async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
        if not exc.is_operational:
            logger.error(
                "Unexpected error",
                error=exc,
                context={"path": str(request.url.path)},
            )
            sentry_sdk.capture_exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled exception",
            error=exc,
            context={"path": str(request.url.path)},
        )
        sentry_sdk.capture_exception(exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    from app.core.middleware import RequestIdMiddleware

    application.add_middleware(RequestIdMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from app.routers import api_router
    from app.routers.amp import router as amp_router
    from app.routers.seo import router as seo_router
    from app.routers.tools.fileshare import download_router as file_download_router
    from app.routers.tools.urlshortener import redirect_router

    application.include_router(api_router, prefix="/api")
    application.include_router(seo_router)
    application.include_router(amp_router)
    application.include_router(redirect_router)
    application.include_router(file_download_router)

    configure_openapi(application)

    return application


app = create_app()
