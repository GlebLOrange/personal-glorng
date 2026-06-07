"""Celery worker tasks: emails, reminders, sync queue, cleanup."""

import smtplib
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

import sentry_sdk
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
from app.core.utils import format_scheduled_at
from app.db.models.google_sync_queue import SyncStatus
from app.db.models.reminder import Reminder
from app.db.models.task import TaskStatus
from app.db.session import get_session_factory
from app.services.task import complete_past_due_tasks, delete_old_tasks
from app.settings import get_settings
from app.todobot.keyboards.task import reminder_actions
from app.workers.async_runner import run_async
from app.workers.celery_app import celery_app
from app.workers.job_names import JobName

MAX_JOB_TRIES = 3


def log_job_failure(job_name: str, job_try: int, exc: BaseException) -> None:
    """Log job failure; report to Sentry on the final attempt."""
    logger.error(
        "Background job failed",
        error=exc,
        context={"job": job_name, "job_try": job_try, "max_tries": MAX_JOB_TRIES},
    )
    if job_try >= MAX_JOB_TRIES:
        sentry_sdk.capture_exception(exc)


def _retry_or_fail(task: Task, job_name: str, exc: Exception) -> None:
    job_try = task.request.retries + 1
    if job_try >= MAX_JOB_TRIES:
        log_job_failure(job_name, job_try, exc)
        raise
    logger.warning(
        "Retrying background job",
        context={"job": job_name, "job_try": job_try, "defer_seconds": 60 * job_try},
    )
    raise task.retry(exc=exc, countdown=60 * job_try) from exc


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


async def send_verification_email(email: str, token: str) -> None:
    await _send_email(
        email,
        token,
        "Verify your email - Gleb Y.",
        render_verification_email,
        render_verification_email_plain,
    )


async def send_reset_email(email: str, token: str) -> None:
    await _send_email(
        email,
        token,
        "Password reset - Gleb Y.",
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
    session_factory = get_session_factory()
    async with session_factory() as db:
        count = await complete_past_due_tasks(db)
        if count:
            await db.commit()
            logger.info(
                "Past-due tasks auto-completed",
                context={"count": count},
            )


async def cleanup_old_tasks() -> None:
    """Delete tasks older than 4 months."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        deleted = await delete_old_tasks(db, months=4)
        await db.commit()
        if deleted:
            logger.info("Old tasks cleaned up", context={"deleted": deleted})


async def cleanup_expired_shares() -> None:
    """Delete expired file-share rows and disk files."""
    from app.services import fileshare as fileshare_svc

    session_factory = get_session_factory()
    async with session_factory() as db:
        stats = await fileshare_svc.cleanup_expired(db)
        await db.commit()
        if stats["deleted_rows"] or stats["errors"]:
            logger.info("Expired file shares cleaned up", context=stats)


async def process_sync_queue() -> None:
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


@celery_app.task(name=JobName.CHECK_OVERDUE_TASKS, ignore_result=True)
def check_overdue_tasks_task() -> None:
    run_async(check_overdue_tasks())


@celery_app.task(name=JobName.CLEANUP_OLD_TASKS, ignore_result=True)
def cleanup_old_tasks_task() -> None:
    run_async(cleanup_old_tasks())


@celery_app.task(name=JobName.CLEANUP_EXPIRED_SHARES, ignore_result=True)
def cleanup_expired_shares_task() -> None:
    run_async(cleanup_expired_shares())


@celery_app.task(name=JobName.PROCESS_SYNC_QUEUE, ignore_result=True)
def process_sync_queue_task() -> None:
    run_async(process_sync_queue())
