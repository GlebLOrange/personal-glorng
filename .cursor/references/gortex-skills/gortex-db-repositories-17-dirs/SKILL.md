---
name: gortex-db-repositories-17-dirs
description: "Work in the db/repositories +17 dirs area — 656 symbols across 60 files (79% cohesion)"
---

# db/repositories +17 dirs

656 symbols | 60 files | 79% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:zoneinfo.ZoneInfo`
- `external-call::stdlib:jwt`
- `server/app/core/deps.py`
- `server/app/core/utils.py`
- `server/app/db/documents/credential.py`
- `server/app/db/documents/import_row.py`
- `server/app/db/documents/task.py`
- `server/app/db/mongo/counter.py`
- `server/app/db/registry.py`
- `server/app/db/repositories/base.py`
- `server/app/db/repositories/credential.py`
- `server/app/db/repositories/data_import.py`
- `server/app/db/repositories/expense.py`
- `server/app/db/repositories/fileshare.py`
- `server/app/db/repositories/health_checker.py`
- `server/app/db/repositories/news.py`
- `server/app/db/repositories/qr_code.py`
- `server/app/db/repositories/recipe.py`
- `server/app/db/repositories/search.py`
- `server/app/db/repositories/task.py`
- `server/app/db/repositories/url.py`
- `server/app/db/repositories/user.py`
- `server/app/db/seed/builders/demo.py`
- `server/app/db/seed/builders/task.py`
- `server/app/db/seed/demo/tools/tasks.py`
- `server/app/routers/admin/users.py`
- `server/app/routers/tools/tasks_admin.py`
- `server/app/schemas/admin_users.py`
- `server/app/schemas/task.py`
- `server/app/schemas/validators.py`
- `server/app/services/admin_users.py`
- `server/app/services/calendar.py`
- `server/app/services/data_import.py`
- `server/app/services/search_indexers/__init__.py`
- `server/app/services/search_indexers/task.py`
- `server/app/services/task.py`
- `server/app/services/task_intake.py`
- `server/app/todobot/handlers/calendar.py`
- `server/app/todobot/handlers/reminder.py`
- `server/app/todobot/handlers/start.py`
- `server/app/todobot/handlers/task_manage.py`
- `server/app/todobot/main.py`
- `server/app/todobot/states/task.py`
- `server/app/workers/queue.py`
- `server/app/workers/scheduling.py`
- `server/app/workers/tasks.py`
- `server/tests/conftest.py`
- `server/tests/factories.py`
- `server/tests/test_audit_helpers.py`
- `server/tests/test_auth.py`
- `server/tests/test_calendar.py`
- `server/tests/test_fileshare_datetime.py`
- `server/tests/test_news_repository.py`
- `server/tests/test_oneshot.py`
- `server/tests/test_task_service.py`
- `server/tests/test_tasks_admin.py`
- `server/tests/test_todobot_task_handlers.py`
- `server/tests/test_todobot_ux.py`
- `server/tests/test_workers.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | datetime.timezone, sort, reverse, now, find, ... |
| `external-call::dep:zoneinfo.ZoneInfo` | zoneinfo.ZoneInfo |
| `external-call::stdlib:jwt` | jwt |
| `server/app/core/deps.py` | get_task_service, registry, get_job_queue_dep, audit_svc |
| `server/app/core/utils.py` | value, value, format_scheduled_at, as_utc, value, ... |
| `server/app/db/documents/credential.py` | GoogleCredential |
| `server/app/db/documents/import_row.py` | ImportRow |
| `server/app/db/documents/task.py` | created_at, attempts, error_notified, action, last_error, ... |
| `server/app/db/mongo/counter.py` | count, next_sequence_ids, next_sequence_id, db, db, ... |
| `server/app/db/registry.py` | DatabaseRegistry, has_postgres |
| `server/app/db/repositories/base.py` | data, next_id, _col, model, _parse_doc |
| `server/app/db/repositories/credential.py` | get_google_for_telegram_user, data, cred, upsert_google, _google_from_doc, ... |
| `server/app/db/repositories/data_import.py` | batch_id, __init__, after_row_index, offset, ImportRowRepository, ... |
| `server/app/db/repositories/expense.py` | date_from, limit, category, offset, date_to, ... |
| `server/app/db/repositories/fileshare.py` | limit, before, list_expired |
| `server/app/db/repositories/health_checker.py` | until, list_due, now, since, list_for_monitor, ... |
| `server/app/db/repositories/news.py` | list_articles, draft_demo_articles, list_tags, tag, limit, ... |
| `server/app/db/repositories/qr_code.py` | delete_for_created_by, user_id |
| `server/app/db/repositories/recipe.py` | offset, list_recipes, tags, recipe_ids, sort, ... |
| `server/app/db/repositories/search.py` | source_id, search_text, source_type, delete_by_source, visibility, ... |
| `server/app/db/repositories/task.py` | list_overdue_pending, count_sync_by_status, limit, limit, offset, ... |
| `server/app/db/repositories/url.py` | code, user_id, get_by_code, delete_for_created_by |
| `server/app/db/repositories/user.py` | email, search, public_id, list_admin, admin_stats, ... |
| `server/app/db/seed/builders/demo.py` | count, telegram_user_id, seed, build_random_tasks, timezone |
| `server/app/db/seed/builders/task.py` | timezone, seed, build_tasks_for_today, telegram_user_id, count |
| `server/app/db/seed/demo/tools/tasks.py` | actor_id, registry, telegram_user_id, seed_demo_tasks, timezone, ... |
| `server/app/routers/admin/users.py` | registry, _admin, get_user_stats |
| `server/app/routers/tools/tasks_admin.py` | _user, data, add_task_reminder, task_id, svc |
| `server/app/schemas/admin_users.py` | AdminUsersStatsResponse |
| `server/app/schemas/task.py` | StatusHistoryResponse, TaskStatsResponse, TaskReminderCreate, ReminderResponse, TaskDetailResponse, ... |
| `server/app/schemas/validators.py` | value, _normalize_utc_datetime |
| `server/app/services/admin_users.py` | get_users_stats, registry |
| `server/app/services/calendar.py` | cred, reminder_minutes, sync_task_to_google, _reminder_minutes_for_task, task, ... |
| `server/app/services/data_import.py` | records, _build_import_rows, error_rows, batch_id |
| `server/app/services/search_indexers/__init__.py` | _reindex_tasks, registry |
| `server/app/services/search_indexers/task.py` | index_task, registry, task |
| `server/app/services/task.py` | source, q, kwargs, task_detail, description, ... |
| `server/app/services/task_intake.py` | task_svc, __init__, registry |
| `server/app/todobot/handlers/calendar.py` | _oauth_keyboard, reconnect, registry, cmd_connect_calendar, registry, ... |
| `server/app/todobot/handlers/reminder.py` | state, handle_reminder_action, callback, registry, registry, ... |
| `server/app/todobot/handlers/start.py` | message, registry, menu_calendar, state |
| `server/app/todobot/handlers/task_manage.py` | handle_status_update, callback, registry |
| `server/app/todobot/main.py` | registry, _recover_reminders |
| `server/app/todobot/states/task.py` | TaskPostpone |
| `server/app/workers/queue.py` | get_job_queue, JobQueue, task_id, revoke |
| `server/app/workers/scheduling.py` | registry, exclude_id, registry, schedule_reminder, reminder, ... |
| `server/app/workers/tasks.py` | process_sync_queue, check_overdue_tasks |
| `server/tests/conftest.py` | limit, reset_worker_registry, registry, registry, visibility, ... |
| `server/tests/factories.py` | telegram_user_id, _require, create_task, title, task_id, ... |
| `server/tests/test_audit_helpers.py` | test_create_task_records_domain_audit, registry |
| `server/tests/test_auth.py` | test_legacy_access_token_without_sv_is_rejected_by_matcher |
| `server/tests/test_calendar.py` | TestSyncTaskToGoogle, registry, mock_registry_fn, test_create_sets_event_id, test_update_calls_api, ... |
| `server/tests/test_fileshare_datetime.py` | test_as_utc_converts_non_utc_aware_datetime, test_as_utc_handles_naive_datetime, test_format_scheduled_at_uses_settings_timezone, test_local_naive_to_utc_interprets_settings_timezone |
| `server/tests/test_news_repository.py` | _article, tags, test_list_articles_filters_by_tag_and_date_range, published_at, slug, ... |
| `server/tests/test_oneshot.py` | test_month_grid_marks_busy_days, test_event_body_uses_thirty_minute_end |
| `server/tests/test_task_service.py` | registry, test_create_task_sanitizes_via_task_text_fields, registry, test_change_status_rejects_complete_for_future_task, registry, ... |
| `server/tests/test_tasks_admin.py` | test_list_tasks_filters_by_start_end, test_complete_past_due_tasks, registry, registry, registry, ... |
| `server/tests/test_todobot_task_handlers.py` | test_handle_status_update_invalid_payload_is_noop, registry, registry, registry, test_reminder_complete_marks_task_completed, ... |
| `server/tests/test_todobot_ux.py` | registry, test_create_with_sync_always_schedules_at_start, test_create_with_sync_early_plus_at_start, registry, test_reminder_minutes_includes_zero_for_google, ... |
| `server/tests/test_workers.py` | test_schedule_reminder_skips_past_due, mock_get_queue, mock_get_queue, registry, registry, ... |

## Entry Points

- `server/app/db/repositories/task.py::TaskRepository.list_closest_pending`

## Connected Communities

- **tests +7 dirs** (26 cross-edges)
- **tests +5 dirs** (23 cross-edges)
- **app/services +11 dirs · record_domain** (14 cross-edges)
- **. +8 dirs · app.core.logging.logger** (14 cross-edges)
- **app/services +15 dirs** (12 cross-edges)
- **tests +10 dirs** (8 cross-edges)
- **app/services +8 dirs · record** (6 cross-edges)
- **app/schemas +8 dirs** (4 cross-edges)
- **routers/tools +10 dirs** (4 cross-edges)
- **app/services +12 dirs** (3 cross-edges)
- **. +8 dirs · _save_parsed** (3 cross-edges)
- **seed/core +7 dirs** (3 cross-edges)
- **tests +4 dirs** (3 cross-edges)
- **. +12 dirs** (2 cross-edges)
- **. +4 dirs · handle_my_tasks_callback** (2 cross-edges)
- **. +2 dirs · escape** (2 cross-edges)
- **. +5 dirs** (2 cross-edges)
- **routers/tools +2 dirs** (2 cross-edges)
- **app/services +10 dirs** (2 cross-edges)
- **tests +3 dirs** (1 cross-edges)
- **app/core +1 dirs · decode_token** (1 cross-edges)
- **. +1 dirs · _get_user_by_public_id_str** (1 cross-edges)
- **app/schemas +2 dirs · validate_clean_optional** (1 cross-edges)
- **tests +9 dirs** (1 cross-edges)
- **db/repositories +4 dirs** (1 cross-edges)
- **app/services +7 dirs · lower** (1 cross-edges)
- **services/search_indexers +6 dirs** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **db/repositories · _recipe_query** (1 cross-edges)
- **tests +2 dirs · store_google_oauth_state** (1 cross-edges)
- **db/repositories · _expense_query** (1 cross-edges)
- **app/services · remove_by_source** (1 cross-edges)
- **. +1 dirs · _build_service** (1 cross-edges)
- **app/core +7 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-398")
explore(operation:"context", task:"understand db/repositories +17 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/db/repositories/task.py::TaskRepository.list_closest_pending"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
