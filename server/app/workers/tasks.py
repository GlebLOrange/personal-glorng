"""ARQ worker tasks: emails, reminders, sync queue, cleanup."""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from aiogram import Bot
from arq import cron
from arq.connections import RedisSettings

from app.db.session import get_session_factory
from app.core.email import (
    get_email_backend,
    render_reset_email,
    render_verification_email,
)
from app.core.logging import logger
from app.db.models.google_sync_queue import SyncStatus
from app.db.models.reminder import Reminder
from app.db.models.task import TaskStatus
from app.services.task import (
    delete_old_tasks,
    get_overdue_pending_tasks,
)
from app.settings import get_settings
from app.todobot.keyboards.task import completion_options, reminder_actions

# --- Email tasks ---


async def _send_email(
    email: str,
    token: str,
    subject: str,
    render_fn: Callable[[str, str], str],
) -> None:
    settings = get_settings()
    backend = get_email_backend()
    html = render_fn(token, settings.BASE_URL)
    await backend.send(email, subject, html)
    logger.info("Email sent", context={"to": email, "subject": subject})


async def send_verification_email(
    ctx: dict,
    email: str,
    token: str,
) -> None:
    await _send_email(
        email,
        token,
        "Verify your email - gLOrng",
        render_verification_email,
    )


async def send_reset_email(
    ctx: dict,
    email: str,
    token: str,
) -> None:
    await _send_email(
        email,
        token,
        "Password reset - gLOrng",
        render_reset_email,
    )


# --- Reminder tasks ---


async def send_reminder(ctx: dict, reminder_id: int) -> None:
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
            text = f"Reminder: *{task.title}*\nScheduled: {task.scheduled_at[:16]}"
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


# --- Periodic tasks ---


async def check_overdue_tasks(ctx: dict) -> None:
    """Send follow-up for tasks past their scheduled time."""
    settings = get_settings()
    if not settings.TELEGRAM_BOT_TO_DO_TOKEN:
        return

    session_factory = get_session_factory()
    async with session_factory() as db:
        tasks = await get_overdue_pending_tasks(db)
        if not tasks:
            return

        bot = Bot(token=settings.TELEGRAM_BOT_TO_DO_TOKEN)
        try:
            for task in tasks:
                await bot.send_message(
                    chat_id=task.telegram_user_id,
                    text=f"What happened with *{task.title}*?",
                    reply_markup=completion_options(task.id),
                    parse_mode="Markdown",
                )
            logger.info(
                "Overdue check complete",
                context={"count": len(tasks)},
            )
        finally:
            await bot.session.close()


async def cleanup_old_tasks(ctx: dict) -> None:
    """Delete tasks older than 4 months."""
    session_factory = get_session_factory()
    async with session_factory() as db:
        deleted = await delete_old_tasks(db, months=4)
        await db.commit()
        if deleted:
            logger.info("Old tasks cleaned up", context={"deleted": deleted})


async def process_sync_queue(ctx: dict) -> None:
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
    _every_5_min = set(range(0, 60, 5))
    _every_2_min = set(range(0, 60, 2))
    cron_jobs = [
        cron(check_overdue_tasks, minute=_every_5_min),
        cron(cleanup_old_tasks, hour=3, minute=0),
        cron(process_sync_queue, minute=_every_2_min),
    ]
    redis_settings = RedisSettings.from_dsn(get_settings().REDIS_URL)
