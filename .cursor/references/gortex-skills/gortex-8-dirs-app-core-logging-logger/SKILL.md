---
name: gortex-8-dirs-app-core-logging-logger
description: "Work in the . +8 dirs · app.core.logging.logger area — 185 symbols across 44 files (61% cohesion)"
---

# . +8 dirs · app.core.logging.logger

185 symbols | 44 files | 61% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:aiogram.Bot`
- `external-call::dep:app.core.logging.logger`
- `external-call::dep:app.workers.queues.celery_dlq`
- `external-call::dep:app.workers.queues.celery_dlx`
- `external-call::dep:email.mime.multipart.MIMEMultipart`
- `external-call::dep:email.mime.text.MIMEText`
- `external-call::dep:fastapi.responses.HTMLResponse`
- `external-call::dep:google_auth_oauthlib.flow.Flow`
- `external-call::stdlib:smtplib`
- `server/app/core/cache_json.py`
- `server/app/core/deps.py`
- `server/app/core/email.py`
- `server/app/core/logging.py`
- `server/app/core/rate_limit.py`
- `server/app/core/redis.py`
- `server/app/core/telegram.py`
- `server/app/db/seed/core/expenses.py`
- `server/app/db/seed/core/news.py`
- `server/app/db/seed/core/tasks.py`
- `server/app/routers/callbacks.py`
- `server/app/routers/github_public.py`
- `server/app/routers/health.py`
- `server/app/routers/resume.py`
- `server/app/scripts/notify_backup_result.py`
- `server/app/scripts/run_ops_job.py`
- `server/app/services/currency.py`
- `server/app/services/expense.py`
- `server/app/services/github_portfolio.py`
- `server/app/services/resume_export.py`
- `server/app/services/resume_pdf.py`
- `server/app/services/stripe_donations.py`
- `server/app/services/weather.py`
- `server/app/todobot/middlewares/auth.py`
- `server/app/workers/async_runner.py`
- `server/app/workers/celery_app.py`
- `server/app/workers/queues.py`
- `server/app/workers/tasks.py`
- `server/tests/test_celery_conf.py`
- `server/tests/test_email.py`
- `server/tests/test_health.py`
- `server/tests/test_oauth_state.py`
- `server/tests/test_resume_pdf.py`
- `server/tests/test_run_ops_job.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | perf_counter, time.perf_counter, format, multiprocessing, randbelow, ... |
| `external-call::dep:aiogram.Bot` | aiogram.Bot |
| `external-call::dep:app.core.logging.logger` | app.core.logging.logger |
| `external-call::dep:app.workers.queues.celery_dlq` | app.workers.queues.celery_dlq |
| `external-call::dep:app.workers.queues.celery_dlx` | app.workers.queues.celery_dlx |
| `external-call::dep:email.mime.multipart.MIMEMultipart` | email.mime.multipart.MIMEMultipart |
| `external-call::dep:email.mime.text.MIMEText` | email.mime.text.MIMEText |
| `external-call::dep:fastapi.responses.HTMLResponse` | fastapi.responses.HTMLResponse |
| `external-call::dep:google_auth_oauthlib.flow.Flow` | google_auth_oauthlib.flow.Flow |
| `external-call::stdlib:smtplib` | smtplib |
| `server/app/core/cache_json.py` | safe_cache_json_loads, raw |
| `server/app/core/deps.py` | get_currency_service |
| `server/app/core/email.py` | settings, get_email_backend, subject, plain, subject, ... |
| `server/app/core/logging.py` | info, context, message |
| `server/app/core/rate_limit.py` | request, __call__ |
| `server/app/core/redis.py` | ttl, key, key, ttl, value, ... |
| `server/app/core/telegram.py` | text, notify_admin |
| `server/app/db/seed/core/expenses.py` | seed_expenses, registry |
| `server/app/db/seed/core/news.py` | seed_news, registry |
| `server/app/db/seed/core/tasks.py` | registry, settings, owner, seed_tasks |
| `server/app/routers/callbacks.py` | registry, code, google_oauth_callback, state |
| `server/app/routers/github_public.py` | registry, public_github_repos |
| `server/app/routers/health.py` | _check_redis |
| `server/app/routers/resume.py` | download_resume_pdf, registry, get_resume |
| `server/app/scripts/notify_backup_result.py` | detail, status, _notify |
| `server/app/scripts/run_ops_job.py` | run_job, main, name, _usage |
| `server/app/services/currency.py` | get_rates_meta, get_rates, payload, _cache_ttl, payload, ... |
| `server/app/services/expense.py` | __init__, registry, currency_svc |
| `server/app/services/github_portfolio.py` | registry, cache_only, get_public_github_repos, settings |
| `server/app/services/resume_export.py` | resume, resume_dict_for_pdf |
| `server/app/services/resume_pdf.py` | _render_resume_pdf_in_subprocess, resume, resume, get_cached_resume_pdf, clear_resume_pdf_cache, ... |
| `server/app/services/stripe_donations.py` | event, handle_stripe_event |
| `server/app/services/weather.py` | lon, location, _resolve_timezone_info, lat, get_weather |
| `server/app/todobot/middlewares/auth.py` | handler, __call__, event, data |
| `server/app/workers/async_runner.py` | run_async, coro |
| `server/app/workers/celery_app.py` | sender, kwargs, _on_worker_ready |
| `server/app/workers/queues.py` | kwargs, exc, args, task_name, retries, ... |
| `server/app/workers/tasks.py` | exc, exc, email, _retry_countdown, send_reset_email_task, ... |
| `server/tests/test_celery_conf.py` | test_retry_countdown_is_exponential_and_capped |
| `server/tests/test_email.py` | monkeypatch, test_console_backend_logs_metadata_only |
| `server/tests/test_health.py` | monkeypatch, _high_usage, test_check_redis_warns_when_memory_above_85_percent |
| `server/tests/test_oauth_state.py` | test_cache_getdel_returns_value_and_removes_key |
| `server/tests/test_resume_pdf.py` | _timeout, monkeypatch, fake_render, _resume, test_cached_resume_pdf_renders_once |
| `server/tests/test_run_ops_job.py` | test_main_requires_exactly_one_arg, test_run_job_rejects_unknown, monkeypatch |

## Entry Points

- `server/app/routers/callbacks.py::google_oauth_callback`

## Connected Communities

- **app/services +11 dirs · ApiError** (15 cross-edges)
- **tests +10 dirs** (12 cross-edges)
- **tests +17 dirs** (6 cross-edges)
- **seed/core +7 dirs** (6 cross-edges)
- **app/services +15 dirs** (6 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **app/services +12 dirs** (4 cross-edges)
- **app/services +11 dirs · delete** (3 cross-edges)
- **app/services +10 dirs · ValidationError** (3 cross-edges)
- **. +12 dirs** (2 cross-edges)
- **app/services +7 dirs · lower** (2 cross-edges)
- **app/routers +3 dirs** (2 cross-edges)
- **app/services · normalize_location** (2 cross-edges)
- **db/repositories +12 dirs** (1 cross-edges)
- **. +2 dirs · _hash_input** (1 cross-edges)
- **app/core +1 dirs · render_verification_email_plain** (1 cross-edges)
- **app/workers +1 dirs** (1 cross-edges)
- **. +1 dirs · api_error_handler** (1 cross-edges)
- **. +5 dirs · aiogram.types.InlineKeyboardBut…** (1 cross-edges)
- **. +1 dirs · loguru.logger** (1 cross-edges)
- **app/services +10 dirs · create_article** (1 cross-edges)
- **app/scripts +3 dirs** (1 cross-edges)
- **. +4 dirs · select_resume** (1 cross-edges)
- **tests +6 dirs · parse_expense_text** (1 cross-edges)
- **app/services +7 dirs · upsert** (1 cross-edges)
- **app/core +1 dirs · render_verification_email** (1 cross-edges)
- **tests +2 dirs · store_google_oauth_state** (1 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (1 cross-edges)
- **. +3 dirs · decrypt_secret** (1 cross-edges)
- **. +2 dirs · _request_with_headers** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-438")
explore(operation:"context", task:"understand . +8 dirs · app.core.logging.logger", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/routers/callbacks.py::google_oauth_callback"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
