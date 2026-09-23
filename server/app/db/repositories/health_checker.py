"""Repositories for health monitors and check results."""

from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.health_checker import HealthCheckResult, HealthMonitor
from app.db.repositories.base import MongoRepository, _parse_doc


class HealthMonitorRepository(MongoRepository[HealthMonitor]):
    """CRUD for ``health_monitors``."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "health_monitors", HealthMonitor)

    async def list_due(self, *, now: datetime, limit: int) -> list[HealthMonitor]:
        """Return enabled monitors whose next check is due."""
        cursor = (
            self._col()
            .find({"enabled": True, "next_check_at": {"$lte": now}})
            .sort([("next_check_at", 1)])
            .limit(limit)
        )
        return [_parse_doc(HealthMonitor, row) async for row in cursor]

    async def delete_for_created_by(self, user_id: int) -> int:
        """Delete all monitors owned by the given user."""
        result = await self._col().delete_many({"created_by": user_id})
        return int(result.deleted_count)


class HealthCheckResultRepository(MongoRepository[HealthCheckResult]):
    """CRUD for ``health_check_results``."""

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "health_check_results", HealthCheckResult)

    async def list_for_monitor(
        self,
        monitor_id: int,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 288,
    ) -> list[HealthCheckResult]:
        """Return recent results for a monitor, oldest first for charts."""
        query: dict[str, object] = {"monitor_id": monitor_id}
        checked: dict[str, datetime] = {}
        if since is not None:
            checked["$gte"] = since
        if until is not None:
            checked["$lte"] = until
        if checked:
            query["checked_at"] = checked
        cursor = (
            self._col()
            .find(query)
            .sort([("checked_at", -1)])
            .limit(limit)
        )
        rows = [_parse_doc(HealthCheckResult, row) async for row in cursor]
        rows.reverse()
        return rows

    async def count_uptime(self, monitor_id: int) -> tuple[int, int]:
        """Return ``(ok_count, total_count)`` for a monitor."""
        total = await self._col().count_documents({"monitor_id": monitor_id})
        if total == 0:
            return 0, 0
        ok = await self._col().count_documents({"monitor_id": monitor_id, "ok": True})
        return int(ok), int(total)

    async def delete_for_monitor(self, monitor_id: int) -> int:
        """Delete all results for a monitor."""
        result = await self._col().delete_many({"monitor_id": monitor_id})
        return int(result.deleted_count)

    async def delete_for_monitors(self, monitor_ids: list[int]) -> int:
        """Delete results for many monitors."""
        if not monitor_ids:
            return 0
        result = await self._col().delete_many({"monitor_id": {"$in": monitor_ids}})
        return int(result.deleted_count)

    async def delete_older_than(self, cutoff: datetime) -> int:
        """Delete results older than ``cutoff``."""
        result = await self._col().delete_many({"checked_at": {"$lt": cutoff}})
        return int(result.deleted_count)
