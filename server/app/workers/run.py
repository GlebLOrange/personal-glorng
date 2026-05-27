"""Entry point for arq worker that sets up the event loop before arq init."""

import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())

from arq.cli import cli  # noqa: E402

cli()
