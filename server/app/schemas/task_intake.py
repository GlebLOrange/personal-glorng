"""Pydantic schemas for AI task intake."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskDraft(BaseModel):
    title: str | None = None
    scheduled_date: str | None = Field(
        None,
        description="ISO date YYYY-MM-DD",
    )
    scheduled_time: str | None = Field(
        None,
        description="24h time HH:MM",
    )
    description: str | None = None
    location: str | None = None
    reminder_minutes: int | None = None
    assignee_hint: str | None = None


class FieldConfidence(BaseModel):
    title: float = 0.0
    scheduled_date: float = 0.0
    scheduled_time: float = 0.0
    description: float = 0.0
    location: float = 0.0
    reminder_minutes: float = 0.0


class ClarificationQuestion(BaseModel):
    field: str
    question: str


class ExtractionResult(BaseModel):
    draft: TaskDraft
    confidence: FieldConfidence
    questions: list[ClarificationQuestion] = Field(default_factory=list)


class ClarificationTurn(BaseModel):
    field: str
    question: str
    answer: str


class TaskIntakeResponse(BaseModel):
    id: int
    status: str
    draft_json: dict | None
    confidence_json: dict | None
    clarification_turns_json: list | None
    clarification_rounds: int
    task_id: int | None
    inbound_text: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
