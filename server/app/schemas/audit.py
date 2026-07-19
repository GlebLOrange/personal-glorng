from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.common import PaginatedResponse


class AuditEventResponse(BaseModel):
    id: int
    occurred_at: datetime
    category: str
    action: str
    actor_type: str
    actor_id: int | None
    source: str
    resource_type: str | None
    resource_id: int | None
    metadata: dict[str, Any] | None = Field(default=None, validation_alias="metadata_")
    request_id: str | None

    model_config = {"from_attributes": True, "populate_by_name": True}


AuditEventListResponse = PaginatedResponse[AuditEventResponse]
