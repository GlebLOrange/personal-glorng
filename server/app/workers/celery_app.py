"""Celery application and beat schedule."""

import sentry_sdk
from celery import Celery
from celery.schedules import crontab
from celery.signals import task_failure, worker_init, worker_ready

from app.core.logging import logger
from app.settings import get_settings
from app.workers.job_names import JobName


def _init_worker_sentry() -> None:
    settings = get_settings()
    if not settings.sentry_enabled():
        return
    sentry_sdk.init(
        dsn=settings.SERVER_SENTRY_DSN,
        environment=settings.APP_ENV,
        release=settings.SERVER_SENTRY_RELEASE or None,
        send_default_pii=False,
    )


@worker_init.connect
def _on_worker_init(**_kwargs: object) -> None:
    _init_worker_sentry()
    logger.info("Celery worker started", context={"env": get_settings().APP_ENV})


@worker_ready.connect
def _on_worker_ready(sender: object | None = None, **kwargs: object) -> None:
    hostname = getattr(sender, "hostname", "unknown")
    logger.info(
        "Celery worker ready",
        context={"hostname": hostname, "broker_connected": True},
    )


@task_failure.connect
def _on_task_failure(
    sender: object | None = None,
    task_id: str | None = None,
    exception: BaseException | None = None,
    args: tuple[object, ...] | None = None,
    kwargs: dict[str, object] | None = None,
    retries: int = 0,
    **extra: object,
) -> None:
    task_name = getattr(sender, "name", "unknown")
    logger.error(
        "Celery task failed",
        error=exception,
        context={
            "task_id": task_id,
            "task_name": task_name,
            "retries": retries,
            "args": str(args)[:500] if args else None,
            "kwargs": str(kwargs)[:500] if kwargs else None,
        },
    )


def create_celery_app() -> Celery:
    settings = get_settings()
    eager = settings.CELERY_TASK_ALWAYS_EAGER or settings.APP_ENV == "test"
    app = Celery("glorng")
    app.conf.update(
        broker_url=settings.CELERY_BROKER_URL,
        result_backend=None,
        task_ignore_result=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_always_eager=eager,
        timezone="UTC",
        enable_utc=True,
    )
    app.conf.beat_schedule = {
        "check-overdue-tasks": {
            "task": JobName.CHECK_OVERDUE_TASKS,
            "schedule": crontab(minute="*/5"),
        },
        "cleanup-old-tasks": {
            "task": JobName.CLEANUP_OLD_TASKS,
            "schedule": crontab(hour=3, minute=0),
        },
        "cleanup-expired-shares": {
            "task": JobName.CLEANUP_EXPIRED_SHARES,
            "schedule": crontab(hour=3, minute=30),
        },
        "process-sync-queue": {
            "task": JobName.PROCESS_SYNC_QUEUE,
            "schedule": crontab(minute="*/2"),
        },
        "refresh-news-sources": {
            "task": JobName.REFRESH_NEWS_SOURCES,
            "schedule": crontab(minute="*/15"),
        },
    }
    return app


celery_app = create_celery_app()
celery_app.autodiscover_tasks(["app.workers"], force=True)
