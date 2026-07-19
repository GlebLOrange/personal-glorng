"""Broker-agnostic job queue for enqueueing and revoking background work."""

import asyncio
from datetime import datetime
from typing import Any, Protocol

from celery import Celery

from app.core.exceptions import ServiceUnavailableError
from app.core.logging import logger
from app.workers.job_names import JobName
from app.workers.tasks import (
    send_reminder_task,
    send_reset_email_task,
    send_verification_email_task,
)

_MAX_EMAIL_LEN = 254
_MAX_TOKEN_LEN = 512


class JobQueue(Protocol):
    async def enqueue(
        self,
        job: JobName,
        *args: object,
        eta: datetime | None = None,
    ) -> str: ...

    async def revoke(self, task_id: str) -> None: ...


def _sanitize_enqueue_args(job: JobName, args: tuple[object, ...]) -> tuple[Any, ...]:
    if job in {JobName.SEND_VERIFICATION_EMAIL, JobName.SEND_RESET_EMAIL}:
        if len(args) != 2:
            msg = f"{job} requires email and token"
            raise ValueError(msg)
        email = str(args[0]).strip()
        token = str(args[1]).strip()
        if not email or len(email) > _MAX_EMAIL_LEN:
            msg = "Invalid email for background job"
            raise ValueError(msg)
        if not token or len(token) > _MAX_TOKEN_LEN:
            msg = "Invalid token for background job"
            raise ValueError(msg)
        return (email, token)

    if job == JobName.SEND_REMINDER:
        if len(args) != 1:
            msg = "send_reminder requires reminder_id"
            raise ValueError(msg)
        reminder_id = args[0]
        if not isinstance(reminder_id, int) or reminder_id <= 0:
            msg = "reminder_id must be a positive integer"
            raise ValueError(msg)
        return (reminder_id,)

    msg = f"Unsupported on-demand job: {job}"
    raise ValueError(msg)


class CeleryJobQueue:
    """Enqueue and revoke Celery tasks without blocking the event loop."""

    def __init__(self, celery_app: Celery) -> None:
        self._app = celery_app
        self._tasks = {
            JobName.SEND_VERIFICATION_EMAIL: send_verification_email_task,
            JobName.SEND_RESET_EMAIL: send_reset_email_task,
            JobName.SEND_REMINDER: send_reminder_task,
        }

    async def enqueue(
        self,
        job: JobName,
        *args: object,
        eta: datetime | None = None,
    ) -> str:
        try:
            task = self._tasks[job]
            sanitized = _sanitize_enqueue_args(job, args)

            def _apply() -> str:
                result = task.apply_async(args=sanitized, eta=eta)
                return result.id

            return await asyncio.to_thread(_apply)
        except ValueError as exc:
            logger.error(
                "Rejected background job enqueue",
                error=exc,
                context={"job": job},
            )
            raise ServiceUnavailableError(
                "Unable to queue background job",
            ) from exc
        except ServiceUnavailableError:
            raise
        except Exception as exc:
            logger.error(
                "Failed to enqueue job",
                error=exc,
                context={"job": job},
            )
            raise ServiceUnavailableError(
                "Unable to queue background job",
            ) from exc

    async def revoke(self, task_id: str) -> None:
        if not task_id.strip():
            return
        try:

            def _revoke() -> None:
                self._app.control.revoke(task_id, terminate=True)

            await asyncio.to_thread(_revoke)
        except Exception as exc:
            logger.warning(
                "Failed to revoke background job",
                error=exc,
                context={"task_id": task_id},
            )


_queue: JobQueue | None = None


def init_job_queue() -> None:
    """Create the shared job queue (idempotent)."""
    global _queue
    if _queue is not None:
        return
    from app.workers.celery_app import celery_app

    _queue = CeleryJobQueue(celery_app)
    logger.info("Job queue initialized")


async def close_job_queue() -> None:
    """Release the shared job queue."""
    global _queue
    _queue = None
    logger.info("Job queue closed")


def get_job_queue() -> JobQueue:
    """Return the shared queue; raises if not initialized."""
    if _queue is None:
        raise RuntimeError("Job queue not initialized. Call init_job_queue() first.")
    return _queue
