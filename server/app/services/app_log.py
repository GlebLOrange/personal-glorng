from datetime import date

from app.db.documents.app_log import AppLog
from app.db.registry import DatabaseRegistry


class AppLogService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry

    def _repo(self):
        if self.registry.app_logs is None:
            msg = "App log repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.app_logs

    async def list_logs(
        self,
        *,
        level: str | None = None,
        request_id: str | None = None,
        message: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AppLog], int]:
        return await self._repo().list_events(
            level=level,
            request_id=request_id,
            message=message,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            limit=limit,
        )
