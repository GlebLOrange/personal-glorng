"""Unified DB seed orchestrator (admin + mock test data)."""

from app.db.seed.demo.run import seed_demo


async def seed(
    *,
    reset: bool = True,
    skip_if_populated: bool = False,
) -> None:
    """Seed admin/demo users and fixed-volume mock tool data."""
    await seed_demo(reset=reset, skip_if_populated=skip_if_populated)
