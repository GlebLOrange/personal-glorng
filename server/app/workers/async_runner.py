"""Persistent asyncio event loop for Celery worker processes."""

import asyncio
from collections.abc import Coroutine

from celery.signals import worker_process_init, worker_process_shutdown

from app.core.redis import close_redis, init_redis
from app.settings import get_settings

_loop: asyncio.AbstractEventLoop | None = None


@worker_process_init.connect
def _init_worker_loop(**_kwargs: object) -> None:
    global _loop
    _loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_loop)
    _loop.run_until_complete(init_redis(get_settings().REDIS_URL))


@worker_process_shutdown.connect
def _shutdown_worker_loop(**_kwargs: object) -> None:
    global _loop
    if _loop is not None:
        _loop.run_until_complete(close_redis())
        _loop.close()
        _loop = None


def run_async[T](coro: Coroutine[object, object, T]) -> T:
    """Run a coroutine on the worker process event loop."""
    if _loop is None:
        return asyncio.run(coro)
    return _loop.run_until_complete(coro)
