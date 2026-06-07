from datetime import date, datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.audit import AuditEvent
from app.db.mongo.counter import next_sequence_id


def _from_doc(data: dict[str, Any]) -> AuditEvent:
    payload = dict(data)
    payload.pop("_id", None)
    return AuditEvent(
        id=payload["id"],
        occurred_at=payload.get("occurred_at"),
        category=payload["category"],
        action=payload["action"],
        actor_type=payload["actor_type"],
        actor_id=payload.get("actor_id"),
        source=payload["source"],
        resource_type=payload.get("resource_type"),
        resource_id=payload.get("resource_id"),
        metadata_=payload.get("metadata"),
        request_id=payload.get("request_id"),
    )


class AuditRepository:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self.db = db

    async def record(self, event: AuditEvent) -> AuditEvent:
        if not event.id:
            event.id = await next_sequence_id(self.db, "audit_events")
        await self.db.audit_events.insert_one(
            {
                "id": event.id,
                "occurred_at": event.occurred_at,
                "category": event.category,
                "action": event.action,
                "actor_type": event.actor_type,
                "actor_id": event.actor_id,
                "source": event.source,
                "resource_type": event.resource_type,
                "resource_id": event.resource_id,
                "metadata": event.metadata_,
                "request_id": event.request_id,
            },
        )
        return event

    async def list_recent(self, *, limit: int = 50) -> list[AuditEvent]:
        cursor = self.db.audit_events.find().sort("occurred_at", -1).limit(limit)
        return [_from_doc(row) async for row in cursor]

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
        query: dict[str, Any] = {}
        if category:
            query["category"] = category
        if action:
            query["action"] = action
        if date_from or date_to:
            occurred: dict[str, datetime] = {}
            if date_from:
                occurred["$gte"] = datetime.combine(date_from, datetime.min.time())
            if date_to:
                occurred["$lte"] = datetime.combine(date_to, datetime.max.time())
            query["occurred_at"] = occurred

        total = await self.db.audit_events.count_documents(query)
        cursor = (
            self.db.audit_events.find(query)
            .sort("occurred_at", -1)
            .skip(offset)
            .limit(limit)
        )
        items = [_from_doc(row) async for row in cursor]
        return items, total
