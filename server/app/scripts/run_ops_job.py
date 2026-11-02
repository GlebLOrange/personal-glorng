"""Run hand-ops sync or cleanup jobs inside the API process."""

from __future__ import annotations

import sys

from app.core.logging import logger
from app.workers.async_runner import run_async
from app.workers.tasks import (
    cleanup_expired_shares,
    cleanup_health_results,
    cleanup_old_tasks,
    process_sync_queue,
)

_JOBS = frozenset({"sync", "cleanup"})


def _usage() -> str:
    """Return the CLI usage string for SystemExit messages."""
    return "Usage: python -m app.scripts.run_ops_job <sync|cleanup>"


async def _run_cleanup() -> None:
    """One pass of each periodic cleanup coroutine."""
    await cleanup_old_tasks()
    await cleanup_expired_shares()
    await cleanup_health_results()


def run_job(name: str) -> None:
    """Dispatch a named in-process ops job.

    Args:
        name: ``sync`` or ``cleanup``.

    Raises:
        SystemExit: When ``name`` is not a supported job.
    """
    job = name.strip().lower()
    if job not in _JOBS:
        raise SystemExit(_usage())

    if job == "sync":
        run_async(process_sync_queue())
        logger.info("Ops job sync finished")
        return

    run_async(_run_cleanup())
    logger.info("Ops job cleanup finished")


def main() -> None:
    """CLI entry for container ``exec`` from ``scripts/ops_job.sh``."""
    if len(sys.argv) != 2:
        raise SystemExit(_usage())
    run_job(sys.argv[1])


if __name__ == "__main__":
    main()
