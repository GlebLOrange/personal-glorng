from datetime import datetime
from typing import Any

from app.db.documents.base import utc_now


class AppLog:
    def __init__(
        self,
        *,
        id: int,
        occurred_at: datetime | None = None,
        level: str,
        message: str,
        logger: str,
        service: str = "api",
        context: dict[str, Any] | None = None,
        error: str | None = None,
        error_type: str | None = None,
        traceback: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.id = id
        self.occurred_at = occurred_at or utc_now()
        self.level = level
        self.message = message
        self.logger = logger
        self.service = service
        self.context = context
        self.error = error
        self.error_type = error_type
        self.traceback = traceback
        self.request_id = request_id
