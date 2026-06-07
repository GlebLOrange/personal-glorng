from datetime import datetime
from enum import StrEnum
from typing import Any

from app.db.documents.base import utc_now


class AuditCategory(StrEnum):
    AUTH = "auth"
    DOMAIN = "domain"
    SECURITY = "security"
    SYSTEM = "system"


class AuditActorType(StrEnum):
    USER = "user"
    TELEGRAM = "telegram"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"


class AuditSource(StrEnum):
    PUBLIC = "public"
    WEB = "web"
    WEB_ADMIN = "web_admin"
    TODOBOT = "todobot"
    API = "api"
    WORKER = "worker"
    SYSTEM = "system"


class AuditEvent:
    def __init__(
        self,
        *,
        id: int,
        occurred_at: datetime | None = None,
        category: str,
        action: str,
        actor_type: str,
        actor_id: int | None = None,
        source: str,
        resource_type: str | None = None,
        resource_id: int | None = None,
        metadata_: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        self.id = id
        self.occurred_at = occurred_at or utc_now()
        self.category = category
        self.action = action
        self.actor_type = actor_type
        self.actor_id = actor_id
        self.source = source
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.metadata_ = metadata_
        self.request_id = request_id
