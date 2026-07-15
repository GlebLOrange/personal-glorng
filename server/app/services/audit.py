"""Persistent audit trail for security and domain events."""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.core.request_context import request_id_var, user_id_var
from app.db.documents.audit import (
    AuditActorType,
    AuditCategory,
    AuditEvent,
    AuditSource,
)
from app.db.registry import DatabaseRegistry
from app.settings import get_settings


@dataclass
class AuditRecord:
    category: AuditCategory
    action: str
    actor_type: AuditActorType
    source: AuditSource
    actor_id: int | None = None
    resource_type: str | None = None
    resource_id: int | None = None
    metadata: dict[str, Any] | None = field(default=None)
    request_id: str | None = None


def domain_event(
    *,
    action: str,
    resource_type: str,
    resource_id: int,
    actor_id: int | None = None,
    actor_type: AuditActorType = AuditActorType.USER,
    source: AuditSource = AuditSource.WEB_ADMIN,
    metadata: dict[str, Any] | None = None,
) -> AuditRecord:
    """Build a standard domain audit record."""
    return AuditRecord(
        category=AuditCategory.DOMAIN,
        action=action,
        actor_type=actor_type,
        actor_id=actor_id,
        source=source,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata=metadata,
    )


class AuditService:
    def __init__(
        self,
        registry: DatabaseRegistry,
        *,
        postgres_db: AsyncSession | None = None,
    ) -> None:
        self.registry = registry
        self.postgres_db = postgres_db

    def _audit_repo(self):
        if self.registry.audit is None:
            msg = "Audit repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.audit

    async def record_domain(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: int,
        actor_id: int | None = None,
        actor_type: AuditActorType = AuditActorType.USER,
        source: AuditSource = AuditSource.WEB_ADMIN,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """Record a domain mutation with standard category defaults."""
        return await self.record(
            domain_event(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
                metadata=metadata,
            ),
        )

    async def record(self, event: AuditRecord) -> AuditEvent:
        """Persist one audit event, filling correlation fields from context."""
        actor_id = event.actor_id
        if actor_id is None and event.actor_type == AuditActorType.USER:
            actor_id = user_id_var.get()

        request_id = event.request_id or request_id_var.get()

        row = AuditEvent(
            id=0,
            category=event.category.value,
            action=event.action,
            actor_type=event.actor_type.value,
            actor_id=actor_id,
            source=event.source.value,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            metadata_=event.metadata,
            request_id=request_id,
        )
        saved = await self._audit_repo().record(row)

        # Mongo is the source of truth; the Postgres mirror is best-effort so a
        # secondary-store failure never breaks the request or desyncs the trail.
        if self.postgres_db is not None and get_settings().enable_postgres():
            try:
                await self._record_postgres(event, actor_id, request_id)
            except Exception as exc:
                logger.error(
                    "Postgres audit mirror failed; Mongo record retained",
                    error=exc,
                    context={"action": event.action, "category": event.category.value},
                )

        return saved

    async def _record_postgres(
        self,
        event: AuditRecord,
        actor_id: int | None,
        request_id: str | None,
    ) -> None:
        from app.db.models.audit_event import AuditEvent as PgAuditEvent

        if self.postgres_db is None:
            return

        row = PgAuditEvent(
            category=event.category.value,
            action=event.action,
            actor_type=event.actor_type.value,
            actor_id=actor_id,
            source=event.source.value,
            resource_type=event.resource_type,
            resource_id=event.resource_id,
            metadata_=event.metadata,
            request_id=request_id,
        )
        self.postgres_db.add(row)
        await self.postgres_db.flush()

    async def list_events(
        self,
        *,
        category: str | None = None,
        action: str | None = None,
        request_id: str | None = None,
        actor_id: int | None = None,
        resource_type: str | None = None,
        resource_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditEvent], int]:
        return await self._audit_repo().list_events(
            category=category,
            action=action,
            request_id=request_id,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            date_from=date_from,
            date_to=date_to,
            offset=offset,
            limit=limit,
        )
