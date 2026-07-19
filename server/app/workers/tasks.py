"""Celery worker tasks: emails, reminders, sync queue, cleanup."""

import hashlib
import secrets
import smtplib
from collections.abc import Callable, Coroutine
from datetime import UTC, datetime, timedelta
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from celery import Task

from app.core.email import (
    get_email_backend,
    render_reset_email,
    render_reset_email_plain,
    render_verification_email,
    render_verification_email_plain,
)
from app.core.logging import logger
from app.core.redis import cache_delete, cache_set_nx
from app.core.redis_keys import EMAIL_DISPATCH_PREFIX
from app.core.utils import format_scheduled_at
from app.db.documents.task import SyncStatus, TaskStatus
from app.db.worker_registry import get_worker_registry
from app.services.task import complete_past_due_tasks, delete_old_tasks
from app.settings import get_settings
from app.todobot.keyboards.task import reminder_actions
from app.workers.async_runner import run_async
from app.workers.celery_app import celery_app
from app.workers.job_names import JobName
from app.workers.queues import publish_dead_letter

MAX_JOB_TRIES = 3
_EMAIL_DISPATCH_TTL = {
    "verify": 60 * 60 * 25,  # verification JWT is 24h
    "reset": 60 * 60 * 2,  # reset JWT is 1h
}


def log_job_failure(job_name: str, job_try: int, exc: BaseException) -> None:
    """Log job failure on the final attempt (Sentry via StructuredLogger)."""
    logger.error(
        "Background job failed",
        error=exc,
        context={"job": job_name, "job_try": job_try, "max_tries": MAX_JOB_TRIES},
    )


def _retry_countdown(job_try: int) -> int:
    """Exponential backoff with jitter, capped at 10 minutes."""
    base = min(600, (2**job_try) * 30)
    return base + secrets.randbelow(16)


def _retry_or_fail(task: Task, job_name: str, exc: Exception) -> None:
    job_try = task.request.retries + 1
    if job_try >= MAX_JOB_TRIES:
        log_job_failure(job_name, job_try, exc)
        publish_dead_letter(
            task_name=job_name,
            task_id=task.request.id,
            args=task.request.args,
            kwargs=task.request.kwargs,
            retries=task.request.retries,
            exc=exc,
        )
        raise
    countdown = _retry_countdown(job_try)
    logger.warning(
        "Retrying background job",
        context={"job": job_name, "job_try": job_try, "defer_seconds": countdown},
    )
    raise task.retry(exc=exc, countdown=countdown) from exc


def _email_dispatch_key(purpose: str, token: str) -> str:
    digest = hashlib.sha256(token.encode()).hexdigest()
    return f"{EMAIL_DISPATCH_PREFIX}{purpose}:{digest}"


# --- Email tasks ---


async def _send_email(
    email: str,
    token: str,
    purpose: str,
    subject: str,
    render_html_fn: Callable[[str, str], str],
    render_plain_fn: Callable[[str, str], str],
) -> None:
    """Send email once per token. Claim before send; release claim on failure."""
    key = _email_dispatch_key(purpose, token)
    ttl = _EMAIL_DISPATCH_TTL[purpose]
    claimed = await cache_set_nx(key, "1", ttl)
    if not claimed:
        logger.info(
            "Skipping duplicate email dispatch",
            context={"to": email, "purpose": purpose},
        )
        return

    settings = get_settings()
    backend = get_email_backend()
    html = render_html_fn(token, settings.BASE_URL)
    plain = render_plain_fn(token, settings.BASE_URL)
    try:
        await backend.send(email, subject, html, plain)
    except Exception:
        await cache_delete(key)
        raise
    logger.info("Email sent", context={"to": email, "subject": subject})


async def send_verification_email(email: str, token: str) -> None:
    await _send_email(
        email,
        token,
        "verify",
        "Verify your email - Gleb.Y",
        render_verification_email,
        render_verification_email_plain,
    )


async def send_reset_email(email: str, token: str) -> None:
    await _send_email(
        email,
        token,
        "reset",
        "Password reset - Gleb.Y",
        render_reset_email,
        render_reset_email_plain,
    )


@celery_app.task(
    bind=True,
    name=JobName.SEND_VERIFICATION_EMAIL,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def send_verification_email_task(self: Task, email: str, token: str) -> None:
    try:
        run_async(send_verification_email(email, token))
    except (smtplib.SMTPException, OSError) as exc:
        _retry_or_fail(self, JobName.SEND_VERIFICATION_EMAIL, exc)


@celery_app.task(
    bind=True,
    name=JobName.SEND_RESET_EMAIL,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def send_reset_email_task(self: Task, email: str, token: str) -> None:
    try:
        run_async(send_reset_email(email, token))
    except (smtplib.SMTPException, OSError) as exc:
        _retry_or_fail(self, JobName.SEND_RESET_EMAIL, exc)


# --- Reminder tasks ---


async def send_reminder(reminder_id: int) -> None:
    """Send a Telegram reminder message for a scheduled reminder."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TO_DO_TOKEN:
        logger.warning("No bot token, skipping reminder")
        return

    registry = await get_worker_registry()
    if registry.tasks is None:
        logger.warning("Tasks repository unavailable, skipping reminder")
        return

    rem = await registry.tasks.get_reminder(reminder_id)
    if not rem or rem.sent:
        return

    task = await registry.tasks.get_or_none(rem.task_id)
    if not task or task.status != TaskStatus.PENDING:
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TO_DO_TOKEN)
    try:
        scheduled = format_scheduled_at(task.scheduled_at)
        text = f"Reminder: *{task.title}*\nScheduled: {scheduled}"
        if task.location:
            text += f"\nLocation: {task.location}"

        await bot.send_message(
            chat_id=task.telegram_user_id,
            text=text,
            reply_markup=reminder_actions(task.id),
            parse_mode="Markdown",
        )
        await registry.tasks.update_reminder(rem.id, sent=True)
        logger.info(
            "Reminder sent",
            context={"reminder_id": rem.id, "task_id": task.id},
        )
    finally:
        await bot.session.close()


@celery_app.task(
    bind=True,
    name=JobName.SEND_REMINDER,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def send_reminder_task(self: Task, reminder_id: int) -> None:
    try:
        run_async(send_reminder(reminder_id))
    except TelegramAPIError as exc:
        _retry_or_fail(self, JobName.SEND_REMINDER, exc)


# --- Periodic tasks ---


async def check_overdue_tasks() -> None:
    """Auto-complete pending tasks past their scheduled time."""
    registry = await get_worker_registry()
    count = await complete_past_due_tasks(registry)
    if count:
        logger.info(
            "Past-due tasks auto-completed",
            context={"count": count},
        )


async def cleanup_old_tasks() -> None:
    """Delete tasks older than 4 months."""
    registry = await get_worker_registry()
    deleted = await delete_old_tasks(registry, months=4)
    if deleted:
        logger.info("Old tasks cleaned up", context={"deleted": deleted})


async def cleanup_expired_shares() -> None:
    """Delete expired file-share rows and disk files."""
    from app.services import fileshare as fileshare_svc

    registry = await get_worker_registry()
    stats = await fileshare_svc.cleanup_expired(registry)
    if stats["deleted_rows"] or stats["errors"]:
        logger.info("Expired file shares cleaned up", context=stats)


async def process_sync_queue() -> None:
    """Process pending Google Calendar sync items."""
    registry = await get_worker_registry()
    if registry.tasks is None:
        return

    now = datetime.now(UTC)
    items = await registry.tasks.list_pending_sync_due(now=now, limit=10)

    for item in items:
        try:
            from app.services.calendar import sync_task_to_google

            await sync_task_to_google(registry, item)
            item.status = SyncStatus.COMPLETED
        except Exception as exc:
            item.attempts += 1
            item.last_error = str(exc)[:500]
            if item.attempts >= 5:
                item.status = SyncStatus.FAILED
                logger.error(
                    "Sync permanently failed",
                    context={
                        "queue_id": item.id,
                        "error": str(exc)[:200],
                    },
                )
            else:
                backoff = [60, 300, 900, 3600]
                delay = backoff[min(item.attempts - 1, len(backoff) - 1)]
                item.next_retry_at = now + timedelta(seconds=delay)
        await registry.tasks.update_sync(item)


async def ingest_news() -> None:
    """Ingest trusted news feeds when enabled."""
    settings = get_settings()
    if not settings.NEWS_INGEST_ENABLED:
        return
    from app.services.audit import AuditService
    from app.services.news import NewsService
    from app.services.news_ingest import NewsIngestService

    registry = await get_worker_registry()
    result = await NewsIngestService(
        NewsService(registry, AuditService(registry))
    ).ingest()
    if result.processed or result.failed:
        logger.info("News ingest completed", context=result.model_dump())


async def publish_news_telegram(article_id: int) -> None:
    """Publish one curated news article to Telegram."""
    settings = get_settings()
    if not settings.NEWS_TELEGRAM_BOT_TOKEN or not settings.NEWS_TELEGRAM_CHANNEL_ID:
        return
    from app.services.audit import AuditService
    from app.services.news import NewsService
    from app.services.news_telegram import publish_news_article_to_telegram

    registry = await get_worker_registry()
    news_svc = NewsService(registry, AuditService(registry))
    article = await news_svc.require_article(article_id)
    if article.telegram_message_id is not None:
        logger.info(
            "Skipping duplicate Telegram news publish",
            context={
                "article_id": article_id,
                "telegram_message_id": article.telegram_message_id,
            },
        )
        return
    message_id = await publish_news_article_to_telegram(article)
    await news_svc.set_telegram_message_id(article_id, message_id)


def _run_periodic_task(task: Task, job_name: str, coro_fn: Callable[[], Any]) -> None:
    try:
        run_async(coro_fn())
    except Exception as exc:
        _retry_or_fail(task, job_name, exc)


@celery_app.task(
    bind=True,
    name=JobName.CHECK_OVERDUE_TASKS,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def check_overdue_tasks_task(self: Task) -> None:
    _run_periodic_task(self, JobName.CHECK_OVERDUE_TASKS, check_overdue_tasks)


@celery_app.task(
    bind=True,
    name=JobName.CLEANUP_OLD_TASKS,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def cleanup_old_tasks_task(self: Task) -> None:
    _run_periodic_task(self, JobName.CLEANUP_OLD_TASKS, cleanup_old_tasks)


@celery_app.task(
    bind=True,
    name=JobName.CLEANUP_EXPIRED_SHARES,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def cleanup_expired_shares_task(self: Task) -> None:
    _run_periodic_task(self, JobName.CLEANUP_EXPIRED_SHARES, cleanup_expired_shares)


@celery_app.task(
    bind=True,
    name=JobName.PROCESS_SYNC_QUEUE,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def process_sync_queue_task(self: Task) -> None:
    _run_periodic_task(self, JobName.PROCESS_SYNC_QUEUE, process_sync_queue)


@celery_app.task(
    bind=True,
    name=JobName.INGEST_NEWS,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def ingest_news_task(self: Task) -> None:
    _run_periodic_task(self, JobName.INGEST_NEWS, ingest_news)


@celery_app.task(
    bind=True,
    name=JobName.PUBLISH_NEWS_TELEGRAM,
    max_retries=MAX_JOB_TRIES - 1,
    ignore_result=True,
)
def publish_news_telegram_task(self: Task, article_id: int) -> None:
    def _publish() -> Coroutine[object, object, None]:
        return publish_news_telegram(article_id)

    _run_periodic_task(self, JobName.PUBLISH_NEWS_TELEGRAM, _publish)
