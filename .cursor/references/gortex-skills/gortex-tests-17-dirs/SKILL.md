---
name: gortex-tests-17-dirs
description: "Work in the tests +17 dirs area — 665 symbols across 61 files (80% cohesion)"
---

# tests +17 dirs

665 symbols | 61 files | 80% cohesion

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
- `server/tests/test_search_index.py`
- `server/tests/test_task_service.py`
- `server/tests/test_tasks_admin.py`
- `server/tests/test_todobot_task_handlers.py`
- `server/tests/test_todobot_ux.py`
- `server/tests/test_workers.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | find, sort, now, reverse, datetime.timedelta, ... |
| `external-call::dep:zoneinfo.ZoneInfo` | zoneinfo.ZoneInfo |
| `external-call::stdlib:jwt` | jwt |
| `server/app/core/deps.py` | get_job_queue_dep, get_task_service, registry, audit_svc |
| `server/app/core/utils.py` | value, value, value, calendar_datetime, format_scheduled_at, ... |
| `server/app/db/documents/credential.py` | GoogleCredential |
| `server/app/db/documents/import_row.py` | ImportRow |
| `server/app/db/documents/task.py` | GoogleSyncQueue, TaskStatusHistory, TaskStatus, SyncAction, SyncStatus, ... |
| `server/app/db/mongo/counter.py` | name, next_sequence_id, db, name, count, ... |
| `server/app/db/registry.py` | has_postgres, DatabaseRegistry |
| `server/app/db/repositories/base.py` | doc_id, _parse_doc, next_id, get_or_none, _col, ... |
| `server/app/db/repositories/credential.py` | get_google_for_telegram_user, data, cred, _google_from_doc, upsert_google, ... |
| `server/app/db/repositories/data_import.py` | list_for_batch, after_row_index, db, limit, __init__, ... |
| `server/app/db/repositories/expense.py` | list_expenses, date_from, limit, date_to, sort, ... |
| `server/app/db/repositories/fileshare.py` | limit, list_expired, before |
| `server/app/db/repositories/health_checker.py` | list_for_monitor, count_uptime, monitor_id, limit, since, ... |
| `server/app/db/repositories/news.py` | list_articles, limit, source_url, enabled, limit, ... |
| `server/app/db/repositories/qr_code.py` | user_id, delete_for_created_by |
| `server/app/db/repositories/recipe.py` | list_recipes, limit, sort, offset, recipe_ids, ... |
| `server/app/db/repositories/search.py` | limit, search_text, delete_by_source, visibility, source_id, ... |
| `server/app/db/repositories/task.py` | count_sync_queue, start, enqueue_sync, TaskRepository, limit, ... |
| `server/app/db/repositories/url.py` | delete_for_created_by, user_id, code, get_by_code |
| `server/app/db/repositories/user.py` | db, list_all, delete, email, admin_stats, ... |
| `server/app/db/seed/builders/demo.py` | timezone, telegram_user_id, seed, count, build_random_tasks |
| `server/app/db/seed/builders/task.py` | count, build_tasks_for_today, seed, timezone, telegram_user_id |
| `server/app/db/seed/demo/tools/tasks.py` | seed_demo_tasks, actor_id, registry, timezone, count, ... |
| `server/app/routers/admin/users.py` | registry, _admin, get_user_stats |
| `server/app/routers/tools/tasks_admin.py` | data, _user, add_task_reminder, data, create_task, ... |
| `server/app/schemas/admin_users.py` | AdminUsersStatsResponse |
| `server/app/schemas/task.py` | StatusHistoryResponse, TaskReminderCreate, SyncQueueResponse, ReminderResponse, TaskDetailResponse, ... |
| `server/app/schemas/validators.py` | value, _normalize_utc_datetime |
| `server/app/services/admin_users.py` | registry, get_users_stats |
| `server/app/services/calendar.py` | _reminder_minutes_for_task, _create_event_sync, reminder_minutes, _build_event_body, registry, ... |
| `server/app/services/data_import.py` | error_rows, records, batch_id, _build_import_rows |
| `server/app/services/search_indexers/__init__.py` | registry, _reindex_tasks |
| `server/app/services/search_indexers/task.py` | task, registry, registry, task_id, remove_task, ... |
| `server/app/services/task.py` | registry, registry, sync_calendar_for_telegram_user, kwargs, title, ... |
| `server/app/services/task_intake.py` | task_svc, __init__, registry |
| `server/app/todobot/handlers/calendar.py` | message, registry, cmd_month, year, month, ... |
| `server/app/todobot/handlers/reminder.py` | registry, state, registry, callback, message, ... |
| `server/app/todobot/handlers/start.py` | message, registry, state, menu_calendar |
| `server/app/todobot/handlers/task_manage.py` | registry, handle_status_update, _task_button_label, callback, task |
| `server/app/todobot/main.py` | _recover_reminders, registry |
| `server/app/todobot/states/task.py` | TaskPostpone |
| `server/app/workers/queue.py` | JobQueue, get_job_queue, revoke, task_id |
| `server/app/workers/scheduling.py` | exclude_id, schedule_reminder, reminder, registry, registry, ... |
| `server/app/workers/tasks.py` | check_overdue_tasks, process_sync_queue |
| `server/tests/conftest.py` | registry, limit, reset_worker_registry, query, db, ... |
| `server/tests/factories.py` | registry, telegram_user_id, status, google_event_id, attr, ... |
| `server/tests/test_audit_helpers.py` | registry, test_create_task_records_domain_audit |
| `server/tests/test_auth.py` | test_legacy_access_token_without_sv_is_rejected_by_matcher |
| `server/tests/test_calendar.py` | test_retries_on_failure, test_preserves_google_event_id, TestBuildEventBody, test_skips_when_task_deleted, TestSyncTaskToGoogle, ... |
| `server/tests/test_fileshare_datetime.py` | test_local_naive_to_utc_interprets_settings_timezone, test_local_naive_to_utc_passes_through_aware, test_format_scheduled_at_uses_settings_timezone, test_as_utc_converts_non_utc_aware_datetime, test_as_utc_handles_naive_datetime |
| `server/tests/test_news_repository.py` | test_list_articles_filters_by_tag_and_date_range, _article, registry, registry, tags, ... |
| `server/tests/test_oneshot.py` | test_month_grid_marks_busy_days, test_event_body_uses_thirty_minute_end |
| `server/tests/test_search_index.py` | registry, test_task_status_change_reindexes |
| `server/tests/test_task_service.py` | test_create_task_rejects_blank_title, registry, registry, registry, registry, ... |
| `server/tests/test_tasks_admin.py` | registry, mock_process, test_process_sync_queue_now_endpoint, auth_client, test_list_tasks_filters_by_start_end, ... |
| `server/tests/test_todobot_task_handlers.py` | registry, test_reminder_complete_marks_task_completed, registry, test_reminder_postpone_reschedules_task, test_handle_status_update_marks_completed, ... |
| `server/tests/test_todobot_ux.py` | test_create_with_sync_early_plus_at_start, registry, test_create_with_sync_always_schedules_at_start, registry, test_reminder_minutes_includes_zero_for_google, ... |
| `server/tests/test_workers.py` | mock_get_queue, registry, registry, test_schedule_reminder_skips_past_due, test_schedule_reminder_enqueues_and_stores_job_id, ... |

## Entry Points

- `server/app/db/repositories/task.py::TaskRepository.list_closest_pending`

## Connected Communities

- **tests +7 dirs** (26 cross-edges)
- **tests +5 dirs** (23 cross-edges)
- **. +8 dirs · app.core.logging.logger** (14 cross-edges)
- **app/services +15 dirs** (12 cross-edges)
- **tests +10 dirs** (9 cross-edges)
- **app/services +11 dirs · delete** (8 cross-edges)
- **app/services +8 dirs · record** (6 cross-edges)
- **app/services +10 dirs · ValidationError** (5 cross-edges)
- **app/db · utc_now** (5 cross-edges)
- **app/schemas +8 dirs** (4 cross-edges)
- **tests +4 dirs** (3 cross-edges)
- **app/services +12 dirs** (3 cross-edges)
- **seed/core +7 dirs** (3 cross-edges)
- **. +8 dirs · _save_parsed** (3 cross-edges)
- **app/services +10 dirs · create_article** (2 cross-edges)
- **app/services +7 dirs · lower** (2 cross-edges)
- **. +5 dirs · aiogram.types.InlineKeyboardBut…** (2 cross-edges)
- **. +2 dirs · escape** (2 cross-edges)
- **app/services +7 dirs · upsert** (2 cross-edges)
- **. +12 dirs** (2 cross-edges)
- **app/core +7 dirs** (1 cross-edges)
- **db/repositories · _expense_query** (1 cross-edges)
- **. +1 dirs · _get_user_by_public_id_str** (1 cross-edges)
- **tests +3 dirs** (1 cross-edges)
- **. +1 dirs · _build_service** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **. +5 dirs · handle_my_tasks_callback** (1 cross-edges)
- **db/repositories · _recipe_query** (1 cross-edges)
- **tests +9 dirs** (1 cross-edges)
- **db/repositories +4 dirs** (1 cross-edges)
- **app/core +1 dirs · decode_token** (1 cross-edges)
- **app/schemas +2 dirs · validate_clean_optional** (1 cross-edges)
- **app/services · remove_by_source** (1 cross-edges)
- **app · update_fields** (1 cross-edges)
- **tests +2 dirs · store_google_oauth_state** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-400")
explore(operation:"context", task:"understand tests +17 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/db/repositories/task.py::TaskRepository.list_closest_pending"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
