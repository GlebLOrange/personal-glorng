---
name: gortex-tests-10-dirs-taskintakeservice
description: "Work in the tests +10 dirs · TaskIntakeService area — 170 symbols across 19 files (83% cohesion)"
---

# tests +10 dirs · TaskIntakeService

170 symbols | 19 files | 83% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:aiogram.types.KeyboardButton`
- `external-call::dep:aiogram.types.ReplyKeyboardMarkup`
- `server/app/core/data_extractor/types.py`
- `server/app/core/deps.py`
- `server/app/core/feature_flags.py`
- `server/app/db/documents/task.py`
- `server/app/db/repositories/task.py`
- `server/app/schemas/task_intake.py`
- `server/app/services/llm_json.py`
- `server/app/services/task_intake.py`
- `server/app/todobot/handlers/expense.py`
- `server/app/todobot/handlers/task_create.py`
- `server/app/todobot/keyboards/menu.py`
- `server/scripts/eval_groq_prompts.py`
- `server/tests/test_schemas_validators.py`
- `server/tests/test_task_intake.py`
- `server/tests/test_todobot_task_handlers.py`
- `server/tests/test_todobot_ux.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | datetime.date, today, isoformat |
| `external-call::dep:aiogram.types.KeyboardButton` | aiogram.types.KeyboardButton |
| `external-call::dep:aiogram.types.ReplyKeyboardMarkup` | aiogram.types.ReplyKeyboardMarkup |
| `server/app/core/data_extractor/types.py` | ExtractionResult |
| `server/app/core/deps.py` | get_task_intake_service, task_svc, registry |
| `server/app/core/feature_flags.py` | is_task_intake_ai_enabled |
| `server/app/db/documents/task.py` | IntakeStatus, TaskIntake, inbound_message_id, confidence_json, draft_json, ... |
| `server/app/db/repositories/task.py` | get_intake, _intake_from_doc, update_intake, intake, intake_id, ... |
| `server/app/schemas/task_intake.py` | ClarificationQuestion, FieldConfidence, ClarificationTurn, ExtractionResult, TaskIntakeResponse, ... |
| `server/app/services/llm_json.py` | groq_api_key |
| `server/app/services/task_intake.py` | cancel_intake, per_page, confirm_intake, intake_id, list_intakes, ... |
| `server/app/todobot/handlers/expense.py` | state, menu_log_expense, callback, registry, message, ... |
| `server/app/todobot/handlers/task_create.py` | intake_id, draft, state, registry, message, ... |
| `server/app/todobot/keyboards/menu.py` | main_menu |
| `server/scripts/eval_groq_prompts.py` | _intake_service |
| `server/tests/test_schemas_validators.py` | test_task_draft_description_allows_5000_chars |
| `server/tests/test_task_intake.py` | registry, registry, mock_get_queue, registry, test_apply_clarification_appends_turn, ... |
| `server/tests/test_todobot_task_handlers.py` | test_confirm_guided_creates_task_and_sync_queue, mock_process, registry, mock_get_queue |
| `server/tests/test_todobot_ux.py` | test_main_menu_has_quick_and_guided_without_expenses |

## Entry Points

- `server/app/todobot/handlers/task_create.py::handle_reminder_choice`

## Connected Communities

- **todobot/handlers +4 dirs** (8 cross-edges)
- **app/services +15 dirs** (6 cross-edges)
- **app/services +11 dirs · record_domain** (5 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **db/repositories +17 dirs** (4 cross-edges)
- **tests +5 dirs** (4 cross-edges)
- **tests +10 dirs · get_settings** (3 cross-edges)
- **. +4 dirs · handle_my_tasks_callback** (3 cross-edges)
- **app/services +12 dirs** (3 cross-edges)
- **routers/tools +10 dirs** (3 cross-edges)
- **. +5 dirs** (3 cross-edges)
- **app/core +6 dirs** (2 cross-edges)
- **app/schemas +8 dirs** (2 cross-edges)
- **tests +6 dirs · parse_expense_text** (1 cross-edges)
- **app/db · __init__** (1 cross-edges)
- **seed/core +7 dirs** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)
- **app/core +7 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-397")
explore(operation:"context", task:"understand tests +10 dirs · TaskIntakeService", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/todobot/handlers/task_create.py::handle_reminder_choice"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
