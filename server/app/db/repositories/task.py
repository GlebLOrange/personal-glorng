from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.documents.base import utc_now
from app.db.documents.task import (
    GoogleSyncQueue,
    IntakeStatus,
    Reminder,
    SyncAction,
    SyncStatus,
    Task,
    TaskIntake,
    TaskStatus,
    TaskStatusHistory,
)
from app.db.mongo.counter import next_sequence_id
from app.db.repositories.base import MongoRepository, _parse_doc


def _intake_from_doc(data: dict[str, Any]) -> TaskIntake:
    payload = dict(data)
    payload.pop("_id", None)
    return TaskIntake(
        id=payload["id"],
        inbound_message_id=payload["inbound_message_id"],
        status=IntakeStatus(payload["status"]),
        draft_json=payload.get("draft_json"),
        confidence_json=payload.get("confidence_json"),
        clarification_turns_json=payload.get("clarification_turns_json"),
        clarification_rounds=payload.get("clarification_rounds", 0),
        task_id=payload.get("task_id"),
        created_at=payload.get("created_at"),
        updated_at=payload.get("updated_at"),
    )


def _history_from_doc(data: dict[str, Any]) -> TaskStatusHistory:
    payload = dict(data)
    payload.pop("_id", None)
    return TaskStatusHistory(
        id=payload["id"],
        task_id=payload["task_id"],
        old_status=payload["old_status"],
        new_status=payload["new_status"],
        changed_at=payload.get("changed_at"),
    )


def _sync_from_doc(data: dict[str, Any]) -> GoogleSyncQueue:
    payload = dict(data)
    payload.pop("_id", None)
    return GoogleSyncQueue(
        id=payload["id"],
        task_id=payload["task_id"],
        action=SyncAction(payload["action"]),
        attempts=payload.get("attempts", 0),
        last_error=payload.get("last_error"),
        next_retry_at=payload.get("next_retry_at"),
        status=SyncStatus(payload.get("status", SyncStatus.PENDING)),
        created_at=payload.get("created_at"),
        error_notified=payload.get("error_notified", False),
        google_event_id=payload.get("google_event_id"),
    )


class TaskRepository(MongoRepository[Task]):
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        super().__init__(db, "tasks", Task)

    async def list_for_user(
        self,
        telegram_user_id: int,
        *,
        offset: int = 0,
        limit: int = 20,
        status: TaskStatus | None = None,
    ) -> list[Task]:
        query: dict[str, Any] = {"telegram_user_id": telegram_user_id}
        if status is not None:
            query["status"] = status.value
        cursor = (
            self._col().find(query).skip(offset).limit(limit).sort("scheduled_at", 1)
        )
        return [_parse_doc(Task, row) async for row in cursor]

    async def add_status_history(
        self,
        *,
        task_id: int,
        old_status: str,
        new_status: str,
    ) -> TaskStatusHistory:
        doc_id = await next_sequence_id(self.db, "task_status_history")
        entry = TaskStatusHistory(
            id=doc_id,
            task_id=task_id,
            old_status=old_status,
            new_status=new_status,
        )
        await self.db.task_status_history.insert_one(
            {
                "id": entry.id,
                "task_id": entry.task_id,
                "old_status": entry.old_status,
                "new_status": entry.new_status,
                "changed_at": entry.changed_at,
            },
        )
        return entry

    async def list_status_history(self, task_id: int) -> list[TaskStatusHistory]:
        cursor = self.db.task_status_history.find({"task_id": task_id}).sort(
            "changed_at", 1
        )
        return [_history_from_doc(row) async for row in cursor]

    async def create_reminder(
        self,
        *,
        task_id: int,
        remind_at: datetime,
        job_id: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            id=await next_sequence_id(self.db, "reminders"),
            task_id=task_id,
            remind_at=remind_at,
            sent=False,
            job_id=job_id,
        )
        await self.db.reminders.insert_one(reminder.model_dump(mode="python"))
        return reminder

    async def get_reminder(self, reminder_id: int) -> Reminder | None:
        data = await self.db.reminders.find_one({"id": reminder_id})
        if data is None:
            return None
        return _parse_doc(Reminder, data)

    async def list_reminders_for_task(self, task_id: int) -> list[Reminder]:
        cursor = self.db.reminders.find({"task_id": task_id}).sort("remind_at", 1)
        return [_parse_doc(Reminder, row) async for row in cursor]

    async def update_reminder(self, reminder_id: int, **fields: Any) -> Reminder:
        fields["updated_at"] = utc_now()
        result = await self.db.reminders.find_one_and_update(
            {"id": reminder_id},
            {"$set": fields},
            return_document=True,
        )
        if result is None:
            from app.core.exceptions import NotFoundError

            raise NotFoundError(f"Reminder {reminder_id} not found")
        return _parse_doc(Reminder, result)

    async def create_intake(self, intake: TaskIntake) -> TaskIntake:
        if not intake.id:
            intake.id = await next_sequence_id(self.db, "task_intakes")
        await self.db.task_intakes.insert_one(
            {
                "id": intake.id,
                "inbound_message_id": intake.inbound_message_id,
                "status": intake.status.value,
                "draft_json": intake.draft_json,
                "confidence_json": intake.confidence_json,
                "clarification_turns_json": intake.clarification_turns_json,
                "clarification_rounds": intake.clarification_rounds,
                "task_id": intake.task_id,
                "created_at": intake.created_at,
                "updated_at": intake.updated_at,
            },
        )
        return intake

    async def get_intake(self, intake_id: int) -> TaskIntake | None:
        data = await self.db.task_intakes.find_one({"id": intake_id})
        if data is None:
            return None
        return _intake_from_doc(data)

    async def update_intake(self, intake: TaskIntake) -> TaskIntake:
        intake.updated_at = utc_now()
        await self.db.task_intakes.replace_one(
            {"id": intake.id},
            {
                "id": intake.id,
                "inbound_message_id": intake.inbound_message_id,
                "status": intake.status.value,
                "draft_json": intake.draft_json,
                "confidence_json": intake.confidence_json,
                "clarification_turns_json": intake.clarification_turns_json,
                "clarification_rounds": intake.clarification_rounds,
                "task_id": intake.task_id,
                "created_at": intake.created_at,
                "updated_at": intake.updated_at,
            },
        )
        return intake

    async def enqueue_sync(self, entry: GoogleSyncQueue) -> GoogleSyncQueue:
        if not entry.id:
            entry.id = await next_sequence_id(self.db, "google_sync_queue")
        await self.db.google_sync_queue.insert_one(
            {
                "id": entry.id,
                "task_id": entry.task_id,
                "action": entry.action.value,
                "attempts": entry.attempts,
                "last_error": entry.last_error,
                "next_retry_at": entry.next_retry_at,
                "status": entry.status.value,
                "created_at": entry.created_at,
                "error_notified": entry.error_notified,
                "google_event_id": entry.google_event_id,
            },
        )
        return entry

    async def list_pending_sync(self, *, limit: int = 50) -> list[GoogleSyncQueue]:
        cursor = (
            self.db.google_sync_queue.find({"status": SyncStatus.PENDING.value})
            .sort("created_at", 1)
            .limit(limit)
        )
        return [_sync_from_doc(row) async for row in cursor]

    async def list_pending_sync_due(
        self,
        *,
        now: datetime,
        limit: int = 10,
    ) -> list[GoogleSyncQueue]:
        cursor = (
            self.db.google_sync_queue.find(
                {
                    "status": SyncStatus.PENDING.value,
                    "next_retry_at": {"$lte": now},
                },
            )
            .sort("created_at", 1)
            .limit(limit)
        )
        return [_sync_from_doc(row) async for row in cursor]

    async def update_sync(self, entry: GoogleSyncQueue) -> GoogleSyncQueue:
        await self.db.google_sync_queue.replace_one(
            {"id": entry.id},
            {
                "id": entry.id,
                "task_id": entry.task_id,
                "action": entry.action.value,
                "attempts": entry.attempts,
                "last_error": entry.last_error,
                "next_retry_at": entry.next_retry_at,
                "status": entry.status.value,
                "created_at": entry.created_at,
                "error_notified": entry.error_notified,
                "google_event_id": entry.google_event_id,
            },
        )
        return entry

    async def list_sync_queue(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[GoogleSyncQueue]:
        cursor = (
            self.db.google_sync_queue.find()
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )
        return [_sync_from_doc(row) async for row in cursor]

    async def count_sync_queue(self) -> int:
        return await self.db.google_sync_queue.count_documents({})

    async def count_intakes(self) -> int:
        return await self.db.task_intakes.count_documents({})

    async def count_sync_by_status(self, status: SyncStatus) -> int:
        return await self.db.google_sync_queue.count_documents(
            {"status": status.value},
        )

    async def list_failed_sync_for_task(self, task_id: int) -> list[GoogleSyncQueue]:
        cursor = self.db.google_sync_queue.find(
            {"task_id": task_id, "status": SyncStatus.FAILED.value},
        )
        return [_sync_from_doc(row) async for row in cursor]

    async def list_admin(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
        status: str | None = None,
    ) -> list[Task]:
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        cursor = (
            self._col().find(query).sort("created_at", -1).skip(offset).limit(limit)
        )
        return [_parse_doc(Task, row) async for row in cursor]

    async def count_all(self, *, status: str | None = None) -> int:
        query: dict[str, Any] = {}
        if status:
            query["status"] = status
        return await self._col().count_documents(query)

    async def list_overdue_pending(
        self,
        *,
        now: datetime,
        limit: int = 100,
    ) -> list[Task]:
        cursor = (
            self._col()
            .find({"status": TaskStatus.PENDING.value, "scheduled_at": {"$lt": now}})
            .sort("scheduled_at", 1)
            .limit(limit)
        )
        return [_parse_doc(Task, row) async for row in cursor]

    async def list_older_than(
        self, *, cutoff: datetime, limit: int = 100
    ) -> list[Task]:
        cursor = (
            self._col()
            .find({"scheduled_at": {"$lt": cutoff}})
            .sort("scheduled_at", 1)
            .limit(limit)
        )
        return [_parse_doc(Task, row) async for row in cursor]

    async def list_unsent_future_reminders(self, *, now: datetime) -> list[Reminder]:
        cursor = self.db.reminders.find(
            {"sent": False, "remind_at": {"$gt": now}}
        ).sort(
            "remind_at",
            1,
        )
        return [_parse_doc(Reminder, row) async for row in cursor]

    async def delete_unsent_reminders(
        self,
        task_id: int,
        *,
        now: datetime,
        exclude_id: int | None = None,
    ) -> list[Reminder]:
        query: dict[str, Any] = {
            "task_id": task_id,
            "sent": False,
            "remind_at": {"$gt": now},
        }
        if exclude_id is not None:
            query["id"] = {"$ne": exclude_id}
        cursor = self.db.reminders.find(query)
        reminders = [_parse_doc(Reminder, row) async for row in cursor]
        if reminders:
            ids = [reminder.id for reminder in reminders]
            await self.db.reminders.delete_many({"id": {"$in": ids}})
        return reminders

    async def list_intakes_with_text(
        self,
        *,
        offset: int = 0,
        limit: int = 20,
    ) -> list[tuple[TaskIntake, str | None]]:
        cursor = (
            self.db.task_intakes.find().sort("created_at", -1).skip(offset).limit(limit)
        )
        intakes = [_intake_from_doc(row) async for row in cursor]
        inbound_ids = [intake.inbound_message_id for intake in intakes]
        inbound_by_id: dict[int, dict[str, Any]] = {}
        if inbound_ids:
            inbound_cursor = self.db.telegram_inbound_messages.find(
                {"id": {"$in": inbound_ids}},
            )
            inbound_by_id = {row["id"]: row async for row in inbound_cursor}
        return [
            (intake, inbound_by_id.get(intake.inbound_message_id, {}).get("text"))
            for intake in intakes
        ]
