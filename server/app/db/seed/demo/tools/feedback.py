"""Demo feedback seeding."""

from app.db.registry import DatabaseRegistry
from app.db.seed.builders.demo import build_random_feedback


async def seed_demo_feedback(registry: DatabaseRegistry, count: int) -> int:
    """Insert random feedback rows."""
    if registry.feedback is None:
        msg = "Feedback repository is not initialized"
        raise RuntimeError(msg)

    rows = build_random_feedback(count, seed=99)
    for row in rows:
        await registry.feedback.insert(row)
    return len(rows)
