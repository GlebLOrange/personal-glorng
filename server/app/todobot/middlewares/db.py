"""Inject database registry into handler data."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.db.registry import DatabaseRegistry


class MongoRegistryMiddleware(BaseMiddleware):
    def __init__(self, registry: DatabaseRegistry) -> None:
        self._registry = registry

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["registry"] = self._registry
        return await handler(event, data)
