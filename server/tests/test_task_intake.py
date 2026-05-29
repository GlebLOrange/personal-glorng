"""Tests for AI task intake service."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.google_sync_queue import GoogleSyncQueue, SyncStatus
from app.db.models.task_intake import IntakeStatus
from app.schemas.task_intake import ExtractionResult, FieldConfidence, TaskDraft
from app.services.task_intake import TaskIntakeService
from app.settings import get_settings


@pytest.fixture(autouse=True)
def disable_task_intake_ai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TASK_INTAKE_AI_ENABLED", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_nlp_hints_from_message(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    hints = svc.nlp_hints("Tomorrow at 18:00 gym")
    assert hints.get("title") or hints.get("scheduled_date")


@pytest.mark.asyncio
async def test_nlp_extraction_builds_questions_for_missing_fields(
    db: AsyncSession,
) -> None:
    svc = TaskIntakeService(db)
    result = svc._extract_from_nlp("do something important", {})
    assert result.draft.title
    assert any(q.field == "scheduled_date" for q in result.questions)


@pytest.mark.asyncio
async def test_store_inbound_idempotent(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    first = await svc.store_inbound_message(
        telegram_user_id=1,
        telegram_message_id=999,
        chat_id=1,
        text="Meet dentist Friday 10am",
    )
    second = await svc.store_inbound_message(
        telegram_user_id=1,
        telegram_message_id=999,
        chat_id=1,
        text="Meet dentist Friday 10am",
    )
    assert first.id == second.id


@pytest.mark.asyncio
async def test_confirm_intake_creates_task_and_sync_queue(
    db: AsyncSession,
) -> None:
    svc = TaskIntakeService(db)
    inbound = await svc.store_inbound_message(
        telegram_user_id=123,
        telegram_message_id=1001,
        chat_id=123,
        text="Buy milk tomorrow 10:00",
    )
    intake = await svc.create_intake_from_message(inbound)
    intake.draft_json = TaskDraft(
        title="Buy milk",
        scheduled_date="2026-12-01",
        scheduled_time="10:00",
    ).model_dump()
    intake.confidence_json = FieldConfidence(
        title=1.0,
        scheduled_date=1.0,
        scheduled_time=1.0,
    ).model_dump()
    intake.status = IntakeStatus.READY
    db.add(intake)
    await db.flush()

    task = await svc.confirm_intake(
        intake.id,
        telegram_user_id=123,
        reminder_minutes=None,
    )
    await db.commit()

    assert task.title == "Buy milk"
    assert task.intake_id == intake.id

    sync_result = await db.execute(
        select(GoogleSyncQueue).where(GoogleSyncQueue.task_id == task.id),
    )
    sync_item = sync_result.scalar_one()
    assert sync_item.status == SyncStatus.PENDING

    refreshed = await svc.get_intake(intake.id)
    assert refreshed.status == IntakeStatus.CONFIRMED
    assert refreshed.task_id == task.id


@pytest.mark.asyncio
async def test_apply_clarification_appends_turn(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    inbound = await svc.store_inbound_message(
        telegram_user_id=1,
        telegram_message_id=2002,
        chat_id=1,
        text="Call mom",
    )
    intake = await svc.create_intake_from_message(inbound)
    intake.draft_json = TaskDraft(title="Call mom").model_dump()
    intake.confidence_json = FieldConfidence(title=0.9).model_dump()
    intake.status = IntakeStatus.CLARIFYING
    db.add(intake)
    await db.flush()

    with patch.object(
        TaskIntakeService,
        "run_extraction",
        new_callable=AsyncMock,
    ) as mock_extract:
        mock_extract.return_value = ExtractionResult(
            draft=TaskDraft(
                title="Call mom",
                scheduled_date="2026-12-01",
                scheduled_time="09:00",
            ),
            confidence=FieldConfidence(
                title=1.0,
                scheduled_date=1.0,
                scheduled_time=1.0,
            ),
            questions=[],
        )
        await svc.apply_clarification(intake.id, "December 1 at 9am")

    updated = await svc.get_intake(intake.id)
    turns = updated.clarification_turns_json or []
    assert len(turns) == 1
    assert turns[0]["answer"] == "December 1 at 9am"


@pytest.mark.asyncio
async def test_list_intakes_admin(auth_client: AsyncClient) -> None:
    resp = await auth_client.get("/api/tools/tasks/intakes")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_build_questions_respects_threshold(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    draft = TaskDraft(title="Test", scheduled_date="2026-06-01", scheduled_time="10:00")
    conf = FieldConfidence(title=0.5, scheduled_date=1.0, scheduled_time=1.0)
    questions = svc._build_questions(draft, conf, threshold=0.7)
    assert any(q.field == "title" for q in questions)


@pytest.mark.asyncio
async def test_cancel_intake(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    inbound = await svc.store_inbound_message(
        telegram_user_id=1,
        telegram_message_id=3003,
        chat_id=1,
        text="Cancel me",
    )
    intake = await svc.create_intake_from_message(inbound)
    await svc.cancel_intake(intake.id)
    updated = await svc.get_intake(intake.id)
    assert updated.status == IntakeStatus.CANCELLED


@pytest.mark.asyncio
async def test_run_extraction_nlp_path(db: AsyncSession) -> None:
    svc = TaskIntakeService(db)
    inbound = await svc.store_inbound_message(
        telegram_user_id=1,
        telegram_message_id=4004,
        chat_id=1,
        text="Team standup tomorrow 9am at office",
    )
    intake = await svc.create_intake_from_message(inbound)
    result = await svc.run_extraction(intake)
    assert result.draft.title
    assert result.draft.location == "office"
    assert any(q.field == "scheduled_date" for q in result.questions)
