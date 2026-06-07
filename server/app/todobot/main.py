"""Todobot entrypoint -- Telegram polling with FSM persistence."""

import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.types import BotCommand

from app.core.logging import logger
from app.db.worker_registry import get_worker_registry
from app.services.task import get_unsent_reminders
from app.settings import get_settings
from app.todobot.handlers import (
    calendar,
    expense,
    reminder,
    start,
    task_create,
    task_manage,
)
from app.todobot.middlewares.auth import AllowedUserMiddleware
from app.todobot.middlewares.db import MongoRegistryMiddleware
from app.workers.queue import close_job_queue, init_job_queue
from app.workers.scheduling import schedule_reminder


def _build_dispatcher(registry) -> Dispatcher:
    settings = get_settings()
    storage = RedisStorage.from_url(
        settings.REDIS_URL,
        key_builder=DefaultKeyBuilder(prefix="todobot_fsm"),
    )
    dp = Dispatcher(storage=storage)

    dp.message.middleware(MongoRegistryMiddleware(registry))
    dp.callback_query.middleware(MongoRegistryMiddleware(registry))

    dp.message.middleware(AllowedUserMiddleware())

    dp.include_router(start.router)
    dp.include_router(expense.router)
    dp.include_router(task_create.router)
    dp.include_router(task_manage.router)
    dp.include_router(reminder.router)
    dp.include_router(calendar.router)

    return dp


async def _recover_reminders(registry) -> None:
    """Re-enqueue unsent future reminders after restart."""
    try:
        reminders = await get_unsent_reminders(registry)
        if not reminders:
            return

        for rem in reminders:
            if rem.job_id:
                continue
            await schedule_reminder(registry, rem)
        logger.info(
            "Recovered reminders on startup",
            context={"count": len(reminders)},
        )
    except Exception as exc:
        logger.warning("Skipping reminder recovery", context={"error": str(exc)})


async def main() -> None:
    settings = get_settings()

    if not settings.TELEGRAM_BOT_TO_DO_TOKEN:
        logger.error("TELEGRAM_BOT_TO_DO_TOKEN is not set")
        return

    registry = await get_worker_registry()
    bot = Bot(token=settings.TELEGRAM_BOT_TO_DO_TOKEN)
    dp = _build_dispatcher(registry)

    logger.info(
        "Starting todobot",
        context={"allowed_user_id": settings.TELEGRAM_ALLOWED_USER_ID},
    )

    init_job_queue()
    await _recover_reminders(registry)
    await bot.set_my_commands(
        [
            BotCommand(command="new", description="Create a new task"),
            BotCommand(command="tasks", description="View pending tasks"),
            BotCommand(command="spend", description="Log an expense"),
            BotCommand(command="expenses", description="This month's expenses"),
            BotCommand(command="connect_calendar", description="Link Google Calendar"),
            BotCommand(command="help", description="Show help & menu"),
        ]
    )

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_job_queue()


if __name__ == "__main__":
    asyncio.run(main())
