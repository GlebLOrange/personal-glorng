"""Shared ARQ Redis pool for enqueueing background jobs."""

from typing import Any

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

from app.core.logging import logger
from app.settings import get_settings

_pool: ArqRedis | None = None


async def init_arq_pool() -> None:
    """Create the shared ARQ pool (idempotent)."""
    global _pool
    if _pool is not None:
        return
    settings = get_settings()
    _pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    logger.info("ARQ pool connected")


async def close_arq_pool() -> None:
    """Close the shared ARQ pool."""
    global _pool
    if _pool is None:
        return
    await _pool.aclose()
    _pool = None
    logger.info("ARQ pool closed")


def get_arq_pool() -> ArqRedis:
    """Return the shared pool; raises if not initialized."""
    if _pool is None:
        raise RuntimeError("ARQ pool not initialized. Call init_arq_pool() first.")
    return _pool


async def enqueue_job(
    name: str,
    *args: Any,  # noqa: ANN401
    **kwargs: Any,  # noqa: ANN401
) -> str | None:
    """Enqueue a job; return job id or None on failure."""
    try:
        pool = get_arq_pool()
        job = await pool.enqueue_job(name, *args, **kwargs)
        if job is None:
            logger.error("Failed to enqueue job", context={"job": name})
            return None
        return job.job_id
    except Exception as exc:
        logger.error(
            "Failed to enqueue job",
            error=exc,
            context={"job": name},
        )
        return None


async def abort_job(job_id: str) -> None:
    """Best-effort cancel of a queued/deferred job."""
    try:
        await get_arq_pool().abort_job(job_id)
    except Exception as exc:
        logger.warning(
            "Failed to abort ARQ job",
            error=exc,
            context={"job_id": job_id},
        )
