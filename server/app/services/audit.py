"""Persistent audit trail for security and domain events."""

from dataclasses import dataclass, field
from datetime import date
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.request_context import request_id_var, user_id_var
from app.db.models.audit_event import (
    AuditActorType,
    AuditCategory,
    AuditEvent,
    AuditSource,
)


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


class AuditService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

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
            AuditRecord(
                category=AuditCategory.DOMAIN,
                action=action,
                actor_type=actor_type,
                actor_id=actor_id,
                source=source,
                resource_type=resource_type,
                resource_id=resource_id,
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
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def list_events(
        self,
        *,
        category: str | None = None,
        action: str | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AuditEvent], int]:
        query = select(AuditEvent).order_by(AuditEvent.occurred_at.desc())
        count_query = select(func.count()).select_from(AuditEvent)

        if category:
            query = query.where(AuditEvent.category == category)
            count_query = count_query.where(AuditEvent.category == category)
        if action:
            query = query.where(AuditEvent.action == action)
            count_query = count_query.where(AuditEvent.action == action)
        if date_from:
            query = query.where(AuditEvent.occurred_at >= date_from)
            count_query = count_query.where(AuditEvent.occurred_at >= date_from)
        if date_to:
            query = query.where(AuditEvent.occurred_at <= date_to)
            count_query = count_query.where(AuditEvent.occurred_at <= date_to)

        total = (await self.db.execute(count_query)).scalar_one()
        result = await self.db.execute(query.offset(offset).limit(limit))
        return list(result.scalars().all()), total
