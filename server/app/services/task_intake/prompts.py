"""Task intake extraction prompt and clarification constants."""

from __future__ import annotations

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
    "assignee_hint": string|null
  },
  "confidence": {
    "title": 0.0-1.0,
    "scheduled_date": 0.0-1.0,
    "scheduled_time": 0.0-1.0,
    "description": 0.0-1.0,
    "location": 0.0-1.0
  },
  "questions": [{"field": string, "question": string}]
}
Rules:
- Use timezone context for relative dates (tomorrow, next Friday).
- scheduled_date must be today or future.
- If a rule-based hint is provided, prefer it when consistent with the message.
- Add questions only for required fields (title, scheduled_date, scheduled_time)
  where value is missing or confidence is below 0.7.
- Do not set or ask about reminder timing; reminders are fixed by the app.
- Keep questions short and conversational.
"""

MAX_CLARIFICATION_ROUNDS = 3
REQUIRED_FIELDS = ("title", "scheduled_date", "scheduled_time")
