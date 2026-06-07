"""ARQ worker tasks: emails, reminders, sync queue, cleanup."""

import smtplib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from typing import Any

import sentry_sdk
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from arq import cron
from arq.connections import RedisSettings
from arq.worker import Retry

from app.core.email import (
    get_email_backend,
    render_reset_email,
    render_reset_email_plain,
    render_verification_email,
    render_verification_email_plain,
)
from app.core.logging import logger
from app.core.utils import format_scheduled_at
from app.db.models.google_sync_queue import SyncStatus
from app.db.models.reminder import Reminder
from app.db.models.task import TaskStatus
from app.db.session import get_session_factory
from app.services.task import complete_past_due_tasks, delete_old_tasks
from app.settings import get_settings
from app.todobot.keyboards.task import reminder_actions

MAX_JOB_TRIES = 3


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


def log_job_failure(job_name: str, ctx: dict[str, Any], exc: BaseException) -> None:
    """Log job failure; report to Sentry on the final attempt."""
    job_try = ctx.get("job_try", 1)
    logger.error(
        "Background job failed",
        error=exc,
        context={"job": job_name, "job_try": job_try, "max_tries": MAX_JOB_TRIES},
    )
    if job_try >= MAX_JOB_TRIES:
        sentry_sdk.capture_exception(exc)


def _raise_retry_or_fail(ctx: dict[str, Any], job_name: str, exc: Exception) -> None:
    job_try = ctx.get("job_try", 1)
    if job_try >= MAX_JOB_TRIES:
        log_job_failure(job_name, ctx, exc)
        raise
    logger.warning(
        "Retrying background job",
        context={"job": job_name, "job_try": job_try, "defer_seconds": 60 * job_try},
    )
    raise Retry(defer=60 * job_try) from exc


async def worker_startup(ctx: dict[str, Any]) -> None:
    _init_worker_sentry()
    logger.info("ARQ worker started", context={"env": get_settings().APP_ENV})


# --- Email tasks ---


async def _send_email(
    email: str,
    token: str,
    subject: str,
    render_html_fn: Callable[[str, str], str],
    render_plain_fn: Callable[[str, str], str],
) -> None:
    settings = get_settings()
    backend = get_email_backend()
    html = render_html_fn(token, settings.BASE_URL)
    plain = render_plain_fn(token, settings.BASE_URL)
    await backend.send(email, subject, html, plain)
    logger.info("Email sent", context={"to": email, "subject": subject})


async def send_verification_email(
    ctx: dict[str, Any],
    email: str,
    token: str,
) -> None:
    try:
        await _send_email(
            email,
            token,
            "Verify your email - gLOrng",
            render_verification_email,
            render_verification_email_plain,
        )
    except (smtplib.SMTPException, OSError) as exc:
        _raise_retry_or_fail(ctx, "send_verification_email", exc)


async def send_reset_email(
    ctx: dict[str, Any],
    email: str,
    token: str,
) -> None:
    try:
        await _send_email(
            email,
            token,
            "Password reset - gLOrng",
            render_reset_email,
            render_reset_email_plain,
        )
    except (smtplib.SMTPException, OSError) as exc:
        _raise_retry_or_fail(ctx, "send_reset_email", exc)


# --- Reminder tasks ---


async def send_reminder(ctx: dict[str, Any], reminder_id: int) -> None:
    """Send a Telegram reminder message for a scheduled reminder."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TO_DO_TOKEN:
        logger.warning("No bot token, skipping reminder")
        return

    session_factory = get_session_factory()
    async with session_factory() as db:
        from sqlalchemy import select

        result = await db.execute(
            select(Reminder).where(Reminder.id == reminder_id),
        )
        rem = result.scalar_one_or_none()
        if not rem or rem.sent:
            return

        task = rem.task
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
            rem.sent = True
            db.add(rem)
            await db.commit()
            logger.info(
                "Reminder sent",
                context={"reminder_id": rem.id, "task_id": task.id},
            )
        except TelegramAPIError as exc:
            _raise_retry_or_fail(ctx, "send_reminder", exc)
        finally:
            await bot.session.close()


# --- Periodic tasks ---


async def check_overdue_tasks(ctx: dict[str, Any]) -> None:
    """Auto-complete pending tasks past their scheduled time."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        count = await complete_past_due_tasks(db)
        if count:
            await db.commit()
            logger.info(
                "Past-due tasks auto-completed",
                context={"count": count},
            )


async def cleanup_old_tasks(ctx: dict[str, Any]) -> None:
    """Delete tasks older than 4 months."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        deleted = await delete_old_tasks(db, months=4)
        await db.commit()
        if deleted:
            logger.info("Old tasks cleaned up", context={"deleted": deleted})


async def process_sync_queue(ctx: dict[str, Any]) -> None:
    """Process pending Google Calendar sync items."""
    from sqlalchemy import select

    from app.db.models.google_sync_queue import GoogleSyncQueue

    session_factory = get_session_factory()
    async with session_factory() as db:
        now = datetime.now(UTC)
        result = await db.execute(
            select(GoogleSyncQueue)
            .where(
                GoogleSyncQueue.status == SyncStatus.PENDING,
                GoogleSyncQueue.next_retry_at <= now,
            )
            .limit(10),
        )
        items = list(result.scalars().all())

        for item in items:
            try:
                from app.services.calendar import sync_task_to_google

                await sync_task_to_google(db, item)
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
            db.add(item)

        await db.commit()


class WorkerSettings:
    functions = [
        send_verification_email,
        send_reset_email,
        send_reminder,
    ]
    on_startup = worker_startup
    max_tries = MAX_JOB_TRIES
    _every_5_min = set(range(0, 60, 5))
    _every_2_min = set(range(0, 60, 2))
    cron_jobs = [
        cron(check_overdue_tasks, minute=_every_5_min),
        cron(cleanup_old_tasks, hour=3, minute=0),
        cron(process_sync_queue, minute=_every_2_min),
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
