"""Todobot entrypoint -- Telegram polling with FSM persistence."""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BotCommand
from arq import create_pool
from arq.connections import RedisSettings

from app.core.logging import logger
from app.db.session import get_session_factory
from app.services.task import get_unsent_reminders
from app.settings import get_settings
from app.todobot.handlers import calendar, reminder, start, task_create, task_manage
from app.todobot.middlewares.auth import AllowedUserMiddleware
from app.todobot.middlewares.db import DbSessionMiddleware


def _build_dispatcher(redis_url: str) -> Dispatcher:
    storage = RedisStorage.from_url(
        redis_url,
        key_builder=DefaultKeyBuilder(prefix="todobot_fsm"),
    )
    dp = Dispatcher(storage=storage)

    session_factory = get_session_factory()
    dp.message.middleware(DbSessionMiddleware(session_factory))
    dp.callback_query.middleware(DbSessionMiddleware(session_factory))

    dp.message.middleware(AllowedUserMiddleware())

    dp.include_router(start.router)
    dp.include_router(task_create.router)
    dp.include_router(task_manage.router)
    dp.include_router(reminder.router)
    dp.include_router(calendar.router)

    return dp


async def _recover_reminders() -> None:
    """Re-enqueue unsent future reminders after restart."""
    settings = get_settings()
    session_factory = get_session_factory()

    try:
        async with session_factory() as db:
            reminders = await get_unsent_reminders(db)
    except Exception as exc:
        logger.warning("Skipping reminder recovery", context={"error": str(exc)})
        return

    if not reminders:
        return

    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    pool = await create_pool(redis_settings)
    try:
        for rem in reminders:
            await pool.enqueue_job(
                "send_reminder",
                rem.id,
                _defer_until=rem.remind_at,
            )
        logger.info(
            "Recovered reminders on startup",
            context={"count": len(reminders)},
        )
    finally:
        await pool.aclose()


async def main() -> None:
    settings = get_settings()

    if not settings.TELEGRAM_BOT_TO_DO_TOKEN:
        logger.error("TELEGRAM_BOT_TO_DO_TOKEN is not set")
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TO_DO_TOKEN)
    dp = _build_dispatcher(settings.REDIS_URL)

    logger.info(
        "Starting todobot",
        context={"allowed_user_id": settings.TELEGRAM_ALLOWED_USER_ID},
    )

    await _recover_reminders()
    await bot.set_my_commands(
        [
            BotCommand(command="new", description="Create a new task"),
            BotCommand(command="tasks", description="View pending tasks"),
            BotCommand(command="connect_calendar", description="Link Google Calendar"),
            BotCommand(command="help", description="Show help & menu"),
        ]
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
