from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.schemas.common import PaginatedResponse


class AppLogResponse(BaseModel):
    id: int
    occurred_at: datetime
    level: str
    message: str
    logger: str
    context: dict[str, Any] | None = None
    error: str | None = None
    error_type: str | None = None
    traceback: str | None = None
    request_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


AppLogListResponse = PaginatedResponse[AppLogResponse]
