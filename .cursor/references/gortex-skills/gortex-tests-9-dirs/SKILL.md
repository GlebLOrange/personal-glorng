---
name: gortex-tests-9-dirs
description: "Work in the tests +9 dirs area — 153 symbols across 16 files (83% cohesion)"
---

# tests +9 dirs

153 symbols | 16 files | 83% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `server/app/core/data_extractor/types.py`
- `server/app/core/deps.py`
- `server/app/core/feature_flags.py`
- `server/app/db/documents/task.py`
- `server/app/db/documents/telegram.py`
- `server/app/db/repositories/task.py`
- `server/app/db/repositories/telegram.py`
- `server/app/schemas/task_intake.py`
- `server/app/services/llm_json.py`
- `server/app/services/task_intake.py`
- `server/app/todobot/handlers/task_create.py`
- `server/scripts/eval_groq_prompts.py`
- `server/tests/test_schemas_validators.py`
- `server/tests/test_task_intake.py`
- `server/tests/test_todobot_task_handlers.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | datetime.date, isoformat, today |
| `server/app/core/data_extractor/types.py` | ExtractionResult |
| `server/app/core/deps.py` | registry, task_svc, get_task_intake_service |
| `server/app/core/feature_flags.py` | is_task_intake_ai_enabled |
| `server/app/db/documents/task.py` | TaskIntake, IntakeStatus |
| `server/app/db/documents/telegram.py` | TelegramInboundMessage |
| `server/app/db/repositories/task.py` | update_intake, _intake_from_doc, get_intake, intake, intake_id, ... |
| `server/app/db/repositories/telegram.py` | _from_doc, message_id, telegram_message_id, message, data, ... |
| `server/app/schemas/task_intake.py` | TaskDraft, ClarificationTurn, ExtractionResult, FieldConfidence, ClarificationQuestion, ... |
| `server/app/services/llm_json.py` | groq_api_key |
| `server/app/services/task_intake.py` | run_extraction, telegram_user_id, intake_id, text, hints, ... |
| `server/app/todobot/handlers/task_create.py` | handle_reminder_choice, state, _process_intake_message, _prompt_reminder_or_confirm, message, ... |
| `server/scripts/eval_groq_prompts.py` | _intake_service |
| `server/tests/test_schemas_validators.py` | test_task_draft_description_allows_5000_chars |
| `server/tests/test_task_intake.py` | registry, registry, test_confirm_intake_creates_task_and_sync_queue, mock_get_queue, test_apply_clarification_appends_turn, ... |
| `server/tests/test_todobot_task_handlers.py` | registry, mock_get_queue, mock_process, test_confirm_guided_creates_task_and_sync_queue |

## Entry Points

- `server/app/todobot/handlers/task_create.py::handle_reminder_choice`

## Connected Communities

- **todobot/handlers +4 dirs** (8 cross-edges)
- **tests +17 dirs** (7 cross-edges)
- **app/services +15 dirs** (6 cross-edges)
- **. +8 dirs · _save_parsed** (6 cross-edges)
- **tests +5 dirs** (5 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **. +5 dirs · aiogram.types.InlineKeyboardBut…** (3 cross-edges)
- **app/services +10 dirs · ValidationError** (3 cross-edges)
- **app/schemas +8 dirs** (2 cross-edges)
- **app/services +12 dirs** (2 cross-edges)
- **tests +10 dirs** (2 cross-edges)
- **app/services +11 dirs · delete** (2 cross-edges)
- **app/core +7 dirs** (1 cross-edges)
- **app/db · utc_now** (1 cross-edges)
- **. +5 dirs · handle_my_tasks_callback** (1 cross-edges)
- **seed/core +7 dirs** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-399")
explore(operation:"context", task:"understand tests +9 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/todobot/handlers/task_create.py::handle_reminder_choice"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
