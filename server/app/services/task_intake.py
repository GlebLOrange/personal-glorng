"""AI-driven task intake from Telegram messages."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from typing import Any

from app.core.exceptions import NotFoundError, ValidationError
from app.core.feature_flags import is_task_intake_ai_enabled
from app.core.utils import as_utc, paginate_params
from app.db.documents.task import IntakeStatus, Task, TaskIntake
from app.db.documents.telegram import TelegramInboundMessage
from app.db.registry import DatabaseRegistry
from app.schemas.task_intake import (
    ClarificationQuestion,
    ClarificationTurn,
    ExtractionResult,
    FieldConfidence,
    TaskDraft,
    TaskIntakeResponse,
)
from app.services.llm_json import complete_json, gemini_api_key
from app.services.task import TaskService
from app.settings import get_settings
from app.todobot.utils.nlp import parse_task_input

EXTRACTION_SYSTEM_PROMPT = """\
You extract structured task/reminder data from user messages.
Return JSON with this exact shape:
{
  "draft": {
    "title": string|null,
    "scheduled_date": "YYYY-MM-DD"|null,
    "scheduled_time": "HH:MM"|null,
    "description": string|null,
    "location": string|null,
    "reminder_minutes": integer|null,
    "assignee_hint": string|null
  },
  "confidence": {
    "title": 0.0-1.0,
    "scheduled_date": 0.0-1.0,
    "scheduled_time": 0.0-1.0,
    "description": 0.0-1.0,
    "location": 0.0-1.0,
    "reminder_minutes": 0.0-1.0
  },
  "questions": [{"field": string, "question": string}]
}
Rules:
- Use timezone context for relative dates (tomorrow, next Friday).
- scheduled_date must be today or future.
- If a rule-based hint is provided, prefer it when consistent with the message.
- Add questions only for required fields (title, scheduled_date, scheduled_time)
  where value is missing or confidence is below 0.7.
- reminder_minutes: common values 15, 30, 60, or null if unknown.
- Keep questions short and conversational.
"""

MAX_CLARIFICATION_ROUNDS = 3
REQUIRED_FIELDS = ("title", "scheduled_date", "scheduled_time")


class TaskIntakeService:
    def __init__(self, registry: DatabaseRegistry) -> None:
        self.registry = registry
        self.settings = get_settings()

    def _tasks(self):
        if self.registry.tasks is None:
            msg = "Tasks repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.tasks

    def _telegram(self):
        if self.registry.telegram is None:
            msg = "Telegram repository is not initialized"
            raise RuntimeError(msg)
        return self.registry.telegram

    async def store_inbound_message(
        self,
        *,
        telegram_user_id: int,
        telegram_message_id: int,
        chat_id: int,
        text: str,
        metadata: dict[str, Any] | None = None,
    ) -> TelegramInboundMessage:
        existing = await self._telegram().get_by_telegram_message_id(
            telegram_message_id,
        )
        if found := existing:
            return found

        msg = TelegramInboundMessage(
            id=0,
            telegram_user_id=telegram_user_id,
            telegram_message_id=telegram_message_id,
            chat_id=chat_id,
            text=text,
            metadata_json=metadata,
        )
        try:
            return await self._telegram().create(msg)
        except Exception:
            row = await self._telegram().get_by_telegram_message_id(
                telegram_message_id,
            )
            if row:
                return row
            raise

    async def create_intake_from_message(
        self,
        inbound: TelegramInboundMessage,
    ) -> TaskIntake:
        intake = TaskIntake(
            id=0,
            inbound_message_id=inbound.id,
            status=IntakeStatus.PARSING,
            clarification_turns_json=[],
        )
        return await self._tasks().create_intake(intake)

    async def get_intake(self, intake_id: int) -> TaskIntake:
        intake = await self._tasks().get_intake(intake_id)
        if not intake:
            raise NotFoundError("Task intake not found")
        return intake

    def nlp_hints(self, text: str) -> dict[str, Any]:
        """Rule-based hints from dateparser for hybrid extraction."""
        parsed = parse_task_input(text)
        hints: dict[str, Any] = {}
        if parsed.title:
            hints["title"] = parsed.title
        if parsed.date:
            hints["scheduled_date"] = parsed.date.isoformat()
        if parsed.time:
            hints["scheduled_time"] = parsed.time.strftime("%H:%M")
        if parsed.location:
            hints["location"] = parsed.location
        if parsed.notes:
            hints["description"] = parsed.notes
        return hints

    async def run_extraction(self, intake: TaskIntake) -> ExtractionResult:
        inbound = await self._load_inbound(intake)
        text = inbound.text
        hints = self.nlp_hints(text)
        turns = intake.clarification_turns_json or []

        if is_task_intake_ai_enabled() and gemini_api_key():
            result = await self._extract_with_llm(
                text=text,
                hints=hints,
                turns=turns,
            )
        else:
            result = self._extract_from_nlp(text, hints)

        intake.draft_json = result.draft.model_dump()
        intake.confidence_json = result.confidence.model_dump()
        intake.status = (
            IntakeStatus.CLARIFYING if result.questions else IntakeStatus.READY
        )
        await self._tasks().update_intake(intake)
        return result

    async def apply_clarification(
        self,
        intake_id: int,
        answer: str,
    ) -> ExtractionResult:
        intake = await self.get_intake(intake_id)
        if intake.status not in (IntakeStatus.CLARIFYING, IntakeStatus.READY):
            raise ValidationError("Intake is not awaiting clarification")

        turns: list[dict[str, str]] = list(intake.clarification_turns_json or [])
        pending = self._pending_question(intake)
        if pending:
            turns.append(
                ClarificationTurn(
                    field=pending.field,
                    question=pending.question,
                    answer=answer.strip(),
                ).model_dump(),
            )
        intake.clarification_turns_json = turns
        intake.clarification_rounds = (intake.clarification_rounds or 0) + 1
        await self._tasks().update_intake(intake)

        result = await self.run_extraction(intake)

        if result.questions and intake.clarification_rounds >= MAX_CLARIFICATION_ROUNDS:
            result = self._force_ready(result)
            intake.draft_json = result.draft.model_dump()
            intake.confidence_json = result.confidence.model_dump()
            intake.status = IntakeStatus.READY
            await self._tasks().update_intake(intake)

        return result

    def next_clarification_question(
        self,
        result: ExtractionResult,
    ) -> ClarificationQuestion | None:
        if not result.questions:
            return None
        return result.questions[0]

    def build_confirmation_summary(self, draft: TaskDraft) -> str:
        lines = [f"*Task:* {draft.title or '—'}"]
        if draft.scheduled_date:
            lines.append(f"*Date:* {draft.scheduled_date}")
        if draft.scheduled_time:
            lines.append(f"*Time:* {draft.scheduled_time}")
        if draft.location:
            lines.append(f"*Location:* {draft.location}")
        if draft.description:
            lines.append(f"*Notes:* {draft.description}")
        if draft.reminder_minutes is not None:
            lines.append(f"*Reminder:* {draft.reminder_minutes} min before")
        return "\n".join(lines)

    def draft_from_intake(self, intake: TaskIntake) -> TaskDraft:
        if not intake.draft_json:
            return TaskDraft()
        return TaskDraft.model_validate(intake.draft_json)

    def scheduled_at_from_draft(self, draft: TaskDraft) -> datetime:
        task_date = draft.scheduled_date or date.today().isoformat()
        task_time = draft.scheduled_time or "12:00"
        return as_utc(datetime.fromisoformat(f"{task_date}T{task_time}:00"))

    async def confirm_intake(
        self,
        intake_id: int,
        *,
        telegram_user_id: int,
        reminder_minutes: int | None = None,
    ) -> Task:
        intake = await self.get_intake(intake_id)
        if intake.status == IntakeStatus.CONFIRMED and intake.task_id:
            task = await TaskService(self.registry).get_task(task_id=intake.task_id)
            if task:
                return task

        draft = self.draft_from_intake(intake)
        if not draft.title:
            raise ValidationError("Task title is required")
        if not draft.scheduled_date or not draft.scheduled_time:
            raise ValidationError("Task date and time are required")

        scheduled_at = self.scheduled_at_from_draft(draft)
        mins = (
            reminder_minutes if reminder_minutes is not None else draft.reminder_minutes
        )

        task_svc = TaskService(self.registry)
        task = await task_svc.create_with_sync(
            telegram_user_id=telegram_user_id,
            title=draft.title,
            scheduled_at=scheduled_at,
            description=draft.description,
            location=draft.location,
            reminder_minutes=int(mins) if mins else None,
            intake_id=intake.id,
        )

        intake.status = IntakeStatus.CONFIRMED
        intake.task_id = task.id
        await self._tasks().update_intake(intake)
        return task

    async def cancel_intake(self, intake_id: int) -> None:
        intake = await self.get_intake(intake_id)
        intake.status = IntakeStatus.CANCELLED
        await self._tasks().update_intake(intake)

    async def list_intakes(
        self,
        *,
        page: int = 1,
        per_page: int = 20,
    ) -> list[TaskIntakeResponse]:
        offset, limit = paginate_params(page, per_page)
        rows = await self._tasks().list_intakes_with_text(offset=offset, limit=limit)
        responses: list[TaskIntakeResponse] = []
        for intake, inbound_text in rows:
            responses.append(
                TaskIntakeResponse(
                    id=intake.id,
                    status=intake.status.value,
                    draft_json=intake.draft_json,
                    confidence_json=intake.confidence_json,
                    clarification_turns_json=intake.clarification_turns_json,
                    clarification_rounds=intake.clarification_rounds,
                    task_id=intake.task_id,
                    inbound_text=inbound_text,
                    created_at=intake.created_at,
                    updated_at=intake.updated_at,
                ),
            )
        return responses

    async def _load_inbound(self, intake: TaskIntake) -> TelegramInboundMessage:
        inbound = await self._telegram().get(intake.inbound_message_id)
        if not inbound:
            raise NotFoundError("Inbound message not found")
        return inbound

    def _pending_question(self, intake: TaskIntake) -> ClarificationQuestion | None:
        if not intake.draft_json:
            return None
        conf = FieldConfidence.model_validate(intake.confidence_json or {})
        draft = TaskDraft.model_validate(intake.draft_json)
        result = ExtractionResult(
            draft=draft,
            confidence=conf,
            questions=self._build_questions(draft, conf),
        )
        return self.next_clarification_question(result)

    async def _extract_with_llm(
        self,
        *,
        text: str,
        hints: dict[str, Any],
        turns: list[dict[str, str]],
    ) -> ExtractionResult:
        today = datetime.now(UTC).date().isoformat()
        user_payload = {
            "message": text,
            "timezone": self.settings.TIMEZONE,
            "today": today,
            "rule_based_hints": hints,
            "clarification_history": turns,
        }
        raw = await complete_json(
            api_key=gemini_api_key() or "",
            model=self.settings.GEMINI_CHAT_MODEL,
            system_prompt=EXTRACTION_SYSTEM_PROMPT,
            user_content=json.dumps(user_payload),
            api_base_url=self.settings.GEMINI_API_BASE_URL,
        )
        return self._parse_extraction_payload(raw)

    def _extract_from_nlp(
        self,
        text: str,
        hints: dict[str, Any],
    ) -> ExtractionResult:
        parsed = parse_task_input(text)
        draft = TaskDraft(
            title=hints.get("title") or parsed.title,
            scheduled_date=hints.get("scheduled_date")
            or (parsed.date.isoformat() if parsed.date else None),
            scheduled_time=hints.get("scheduled_time")
            or (parsed.time.strftime("%H:%M") if parsed.time else None),
            description=hints.get("description") or parsed.notes,
            location=hints.get("location") or parsed.location,
        )
        conf = FieldConfidence(
            title=1.0 if draft.title else 0.0,
            scheduled_date=1.0 if draft.scheduled_date else 0.0,
            scheduled_time=1.0 if draft.scheduled_time else 0.0,
            description=1.0 if draft.description else 0.5,
            location=1.0 if draft.location else 0.5,
        )
        questions = self._build_questions(draft, conf)
        return ExtractionResult(draft=draft, confidence=conf, questions=questions)

    def _parse_extraction_payload(self, raw: dict[str, Any]) -> ExtractionResult:
        draft_data = raw.get("draft", {})
        conf_data = raw.get("confidence", {})
        questions_data = raw.get("questions", [])

        draft = TaskDraft.model_validate(draft_data)
        confidence = FieldConfidence.model_validate(conf_data)
        questions = [ClarificationQuestion.model_validate(q) for q in questions_data]
        threshold = self.settings.TASK_INTAKE_CONFIDENCE_THRESHOLD
        if not questions:
            questions = self._build_questions(draft, confidence, threshold)
        return ExtractionResult(
            draft=draft,
            confidence=confidence,
            questions=questions,
        )

    def _build_questions(
        self,
        draft: TaskDraft,
        confidence: FieldConfidence,
        threshold: float | None = None,
    ) -> list[ClarificationQuestion]:
        threshold = threshold or self.settings.TASK_INTAKE_CONFIDENCE_THRESHOLD
        prompts = {
            "title": "What should I call this task?",
            "scheduled_date": "What date should I schedule this for?",
            "scheduled_time": "What time should I remind you?",
        }
        questions: list[ClarificationQuestion] = []
        for field in REQUIRED_FIELDS:
            value = getattr(draft, field, None)
            conf = getattr(confidence, field, 0.0)
            if not value or conf < threshold:
                questions.append(
                    ClarificationQuestion(
                        field=field,
                        question=prompts[field],
                    ),
                )
        return questions

    def _force_ready(self, result: ExtractionResult) -> ExtractionResult:
        draft = result.draft
        if not draft.title:
            draft.title = "Untitled task"
        if not draft.scheduled_date:
            draft.scheduled_date = date.today().isoformat()
        if not draft.scheduled_time:
            draft.scheduled_time = "12:00"
        return ExtractionResult(
            draft=draft,
            confidence=result.confidence,
            questions=[],
        )
