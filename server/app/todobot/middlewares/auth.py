"""Reject messages from non-allowed Telegram users."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.core.logging import logger
from app.settings import get_settings


class AllowedUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message) and event.from_user:
            allowed_id = get_settings().TELEGRAM_ALLOWED_USER_ID
            if allowed_id and event.from_user.id != allowed_id:
                logger.warning(
                    "Unauthorized Telegram user",
                    context={"user_id": event.from_user.id},
                )
                return None
        return await handler(event, data)
