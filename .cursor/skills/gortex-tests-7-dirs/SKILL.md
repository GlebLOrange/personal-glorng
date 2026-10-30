---
name: gortex-tests-7-dirs
description: "Work in the tests +7 dirs area — 186 symbols across 44 files (71% cohesion)"
---

# tests +7 dirs

186 symbols | 44 files | 71% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:aiogram.fsm.context.FSMContext`
- `external-call::dep:aiogram.fsm.storage.base.StorageKey`
- `external-call::dep:aiogram.fsm.storage.memory.MemoryStorage`
- `external-call::dep:aiogram.types.Chat`
- `external-call::dep:aiogram.types.User`
- `external-call::dep:app.main.app`
- `external-call::dep:app.workers.celery_app.celery_app`
- `external-call::dep:redis.asyncio.Redis`
- `external-call::dep:redis.exceptions.ConnectionError`
- `server/app/core/mongodb.py`
- `server/app/core/redis.py`
- `server/app/core/url_safety.py`
- `server/app/db/documents/health_checker.py`
- `server/app/services/health_checker.py`
- `server/app/services/weather.py`
- `server/app/services/world_time.py`
- `server/app/workers/async_runner.py`
- `server/app/workers/broker_health.py`
- `server/scripts/eval_groq_prompts.py`
- `server/tests/conftest.py`
- `server/tests/test_account.py`
- `server/tests/test_auth.py`
- `server/tests/test_broker_health.py`
- `server/tests/test_feedback.py`
- `server/tests/test_health_checker_probe.py`
- `server/tests/test_maintenance.py`
- `server/tests/test_mongodb.py`
- `server/tests/test_oauth_state.py`
- `server/tests/test_redis_init.py`
- `server/tests/test_redis_integration.py`
- `server/tests/test_run_ops_job.py`
- `server/tests/test_sentry_init.py`
- `server/tests/test_stripe_donations.py`
- `server/tests/test_todobot_task_handlers.py`
- `server/tests/test_todobot_ux.py`
- `server/tests/test_tools/test_ai_chat.py`
- `server/tests/test_tools/test_health_checker.py`
- `server/tests/test_url_safety.py`
- `server/tests/test_viddownload.py`
- `server/tests/test_viddownload_ssrf.py`
- `server/tests/test_weather.py`
- `server/tests/test_workers.py`
- `server/tests/test_world_time.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | unittest.mock.AsyncMock, timestamp, MagicMock, AsyncMock, patch, ... |
| `external-call::dep:aiogram.fsm.context.FSMContext` | aiogram.fsm.context.FSMContext |
| `external-call::dep:aiogram.fsm.storage.base.StorageKey` | aiogram.fsm.storage.base.StorageKey |
| `external-call::dep:aiogram.fsm.storage.memory.MemoryStorage` | aiogram.fsm.storage.memory.MemoryStorage |
| `external-call::dep:aiogram.types.Chat` | aiogram.types.Chat |
| `external-call::dep:aiogram.types.User` | aiogram.types.User |
| `external-call::dep:app.main.app` | app.main.app |
| `external-call::dep:app.workers.celery_app.celery_app` | app.workers.celery_app.celery_app |
| `external-call::dep:redis.asyncio.Redis` | redis.asyncio.Redis |
| `external-call::dep:redis.exceptions.ConnectionError` | redis.exceptions.ConnectionError |
| `server/app/core/mongodb.py` | get_mongodb_database, is_mongodb_enabled |
| `server/app/core/redis.py` | url, _connect_redis, close_redis, label, cache_url, ... |
| `server/app/core/url_safety.py` | url, allow_public_ip_literals, max_redirects, request_kwargs, url, ... |
| `server/app/db/documents/health_checker.py` | DnsRecord |
| `server/app/services/health_checker.py` | url, ProbeOutcome, url, hostname, _resolve_dns, ... |
| `server/app/services/weather.py` | payload, enrich_weather_timezone, hours, TimezoneInfo, _utc_offset_hours_from_world_time, ... |
| `server/app/services/world_time.py` | fetch_timezone_time, total_seconds, iana, WorldTimePayload, WorldTimeService, ... |
| `server/app/workers/async_runner.py` | _shutdown_worker_loop, _kwargs |
| `server/app/workers/broker_health.py` | check_broker_connection |
| `server/scripts/eval_groq_prompts.py` | api_key, _chat_completion, base_url, model, user_content, ... |
| `server/tests/conftest.py` | ping, aclose |
| `server/tests/test_account.py` | test_change_email_requires_reverify, auth_client |
| `server/tests/test_auth.py` | admin_user, registry, monkeypatch, test_login_user_dual_writes_audit_to_postgres, client, ... |
| `server/tests/test_broker_health.py` | test_broker_connection_fails_when_broker_raises, test_broker_connection_succeeds_when_broker_accepts |
| `server/tests/test_feedback.py` | mock_notify |
| `server/tests/test_health_checker_probe.py` | test_probe_url_rejects_private_host, test_probe_url_success |
| `server/tests/test_maintenance.py` | auth_client, maintenance_env, monkeypatch, test_run_backup_disabled_never_spawns, asyncio_sleep_brief, ... |
| `server/tests/test_mongodb.py` | test_clear_mongodb_unregisters_helpers, test_bind_mongodb_registers_client_and_database |
| `server/tests/test_oauth_state.py` | client, monkeypatch, test_google_oauth_state_is_one_time_use |
| `server/tests/test_redis_init.py` | test_init_redis_pings_on_startup, test_init_redis_separate_cache_client, test_init_redis_raises_when_ping_fails |
| `server/tests/test_redis_integration.py` | test_real_redis_set_get_roundtrip, test_real_redis_ping |
| `server/tests/test_run_ops_job.py` | test_run_job_sync_calls_process_sync_queue, test_run_job_cleanup_runs_all_cleanups |
| `server/tests/test_sentry_init.py` | test_logger_capture_exception_on_error |
| `server/tests/test_stripe_donations.py` | test_create_checkout_session_sends_donate_metadata |
| `server/tests/test_todobot_task_handlers.py` | user_id, chat_id, data, chat_id, _user, ... |
| `server/tests/test_todobot_ux.py` | registry, test_menu_restart_clears_state_and_sends_welcome |
| `server/tests/test_tools/test_ai_chat.py` | test_groq_service_retries_on_429_then_succeeds, _rate_limited_client, fail_count, groq_chat_service, test_groq_service_raises_after_retry_exhausted, ... |
| `server/tests/test_tools/test_health_checker.py` | admin_user, test_other_users_monitor_forbidden, test_create_monitor, auth_client, client, ... |
| `server/tests/test_url_safety.py` | test_public_http_url_allows_dns_to_public_ip, test_public_http_url_fails_closed_on_dns_error, test_public_http_url_rejects_dns_to_private_ip, test_get_public_http_url_sni_and_relative_redirect |
| `server/tests/test_viddownload.py` | auth_client, monkeypatch, test_viddownload_allowlisted_url_reaches_yt_dlp |
| `server/tests/test_viddownload_ssrf.py` | auth_client, test_viddownload_rejects_unsafe_redirect_target, monkeypatch, monkeypatch, auth_client, ... |
| `server/tests/test_weather.py` | test_enrich_weather_timezone_reenriches_incomplete_wttr_zone, payload, test_enrich_weather_timezone_fallback_when_world_time_fails, _mock_weather_client, test_enrich_weather_timezone_skips_when_fully_enriched, ... |
| `server/tests/test_workers.py` | registry, test_supersede_unsent_reminders_aborts_and_deletes, mock_get_queue |
| `server/tests/test_world_time.py` | test_fetch_timezone_time_from_zoneinfo, test_fetch_timezone_time_rejects_unknown_zone |

## Entry Points

- `server/tests/test_workers.py::test_supersede_unsent_reminders_aborts_and_deletes`

## Connected Communities

- **tests +10 dirs** (13 cross-edges)
- **tests +17 dirs** (13 cross-edges)
- **tests +5 dirs** (13 cross-edges)
- **app/services +11 dirs · ApiError** (9 cross-edges)
- **tests +3 dirs** (9 cross-edges)
- **. +8 dirs · app.core.logging.logger** (8 cross-edges)
- **app/services +7 dirs · lower** (7 cross-edges)
- **app/services +12 dirs** (4 cross-edges)
- **. +1 dirs · _is_blocked_ip** (4 cross-edges)
- **app/services +11 dirs · delete** (4 cross-edges)
- **. +12 dirs** (4 cross-edges)
- **app/services +8 dirs · escape** (3 cross-edges)
- **app/services +15 dirs** (2 cross-edges)
- **tests +2 dirs · store_google_oauth_state** (2 cross-edges)
- **tests +6 dirs · create_user** (2 cross-edges)
- **app/core +2 dirs · GroqChatService** (2 cross-edges)
- **todobot/handlers** (1 cross-edges)
- **tests +1 dirs** (1 cross-edges)
- **. +2 dirs · _canonical_url** (1 cross-edges)
- **scripts +2 dirs · rewrite_python_requirement** (1 cross-edges)
- **app/services +8 dirs · record** (1 cross-edges)
- **routers/tools +3 dirs** (1 cross-edges)
- **app/services · _headers** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-515")
explore(operation:"context", task:"understand tests +7 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/tests/test_workers.py::test_supersede_unsent_reminders_aborts_and_deletes"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
