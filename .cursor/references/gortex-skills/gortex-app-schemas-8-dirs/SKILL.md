---
name: gortex-app-schemas-8-dirs
description: "Work in the app/schemas +8 dirs area — 247 symbols across 46 files (84% cohesion)"
---

# app/schemas +8 dirs

247 symbols | 46 files | 84% cohesion

## When to Use

Use this skill when working on files in:
- `external-call::dep:app.core.pagination.paginate_params`
- `external-call::dep:fastapi.Depends`
- `external-call::dep:fastapi.Query`
- `external-call::dep:fastapi.exceptions.RequestValidationError`
- `server/app/core/pagination.py`
- `server/app/core/utils.py`
- `server/app/db/repositories/base.py`
- `server/app/db/repositories/data_import.py`
- `server/app/db/repositories/expense.py`
- `server/app/db/repositories/news.py`
- `server/app/routers/admin/users.py`
- `server/app/routers/feedback.py`
- `server/app/routers/resume.py`
- `server/app/routers/tools/app_logs.py`
- `server/app/routers/tools/audit.py`
- `server/app/routers/tools/data_extract.py`
- `server/app/routers/tools/expenses.py`
- `server/app/routers/tools/fileshare.py`
- `server/app/routers/tools/health_checker.py`
- `server/app/routers/tools/news.py`
- `server/app/routers/tools/news_sources.py`
- `server/app/routers/tools/qr_generator.py`
- `server/app/routers/tools/recipes.py`
- `server/app/routers/tools/tasks_admin.py`
- `server/app/routers/tools/urlshortener.py`
- `server/app/schemas/admin_users.py`
- `server/app/schemas/app_log.py`
- `server/app/schemas/audit.py`
- `server/app/schemas/common.py`
- `server/app/schemas/data_extract.py`
- `server/app/schemas/date_filters.py`
- `server/app/schemas/feedback.py`
- `server/app/schemas/fileshare.py`
- `server/app/schemas/health_checker.py`
- `server/app/schemas/news.py`
- `server/app/schemas/qr_generator.py`
- `server/app/schemas/task.py`
- `server/app/schemas/task_intake.py`
- `server/app/schemas/url.py`
- `server/app/services/admin_users.py`
- `server/app/services/data_import.py`
- `server/app/services/feedback.py`
- `server/app/services/fileshare.py`
- `server/app/services/health_checker.py`
- `server/app/services/news.py`
- `server/tests/test_pagination.py`

## Key Files

| File | Symbols |
|------|---------|
| `external-call::dep:app.core.pagination.paginate_params` | app.core.pagination.paginate_params |
| `external-call::dep:fastapi.Depends` | fastapi.Depends |
| `external-call::dep:fastapi.Query` | fastapi.Query |
| `external-call::dep:fastapi.exceptions.RequestValidationError` | fastapi.exceptions.RequestValidationError |
| `server/app/core/pagination.py` | items, audit_pagination_params, page, pagination_params_factory, per_page, ... |
| `server/app/core/utils.py` | per_page, paginate_params, page |
| `server/app/db/repositories/base.py` | count, filters |
| `server/app/db/repositories/data_import.py` | imported_by, count_for_user |
| `server/app/db/repositories/expense.py` | category_name, count_expenses_in_category |
| `server/app/db/repositories/news.py` | enabled, count_sources |
| `server/app/routers/admin/users.py` | search, get_users, _admin, registry, status, ... |
| `server/app/routers/feedback.py` | status, page, sort, registry, _user, ... |
| `server/app/routers/resume.py` | projects, skills, sections, get_resume_profile |
| `server/app/routers/tools/app_logs.py` | sort, filters, message, user, svc, ... |
| `server/app/routers/tools/audit.py` | resource_type, request_id, pagination, svc, filters, ... |
| `server/app/routers/tools/data_extract.py` | field_delimiter, format, user, file, field_delimiter, ... |
| `server/app/routers/tools/expenses.py` | export_expenses, category, svc, category, filters, ... |
| `server/app/routers/tools/fileshare.py` | page, user, per_page, registry, list_files |
| `server/app/routers/tools/health_checker.py` | registry, page, user, list_monitors, per_page |
| `server/app/routers/tools/news.py` | page, status, list_news, tag, svc, ... |
| `server/app/routers/tools/news_sources.py` | enabled, per_page, user, page, list_news_sources, ... |
| `server/app/routers/tools/qr_generator.py` | registry, per_page, page, list_saved_qr_codes, user |
| `server/app/routers/tools/recipes.py` | search, sort, svc, page, tag, ... |
| `server/app/routers/tools/tasks_admin.py` | end, sort, list_intakes, svc, q, ... |
| `server/app/routers/tools/urlshortener.py` | per_page, user, registry, list_urls, page |
| `server/app/schemas/admin_users.py` | AdminUserListResponse |
| `server/app/schemas/app_log.py` | AppLogResponse |
| `server/app/schemas/audit.py` | AuditEventResponse |
| `server/app/schemas/common.py` | PaginatedResponse |
| `server/app/schemas/data_extract.py` | ExtractionResultResponse, ImportRowErrorResponse, ImportResultResponse, ImportBatchResponse, ImportBatchListResponse |
| `server/app/schemas/date_filters.py` | month, news_date_filter, DateRangeFilter, date_to, ExpenseDateFilter, ... |
| `server/app/schemas/feedback.py` | FeedbackResponse, FeedbackListResponse |
| `server/app/schemas/fileshare.py` | SharedFileListResponse |
| `server/app/schemas/health_checker.py` | HealthMonitorListResponse |
| `server/app/schemas/news.py` | NewsSourceResponse, NewsSourceListResponse |
| `server/app/schemas/qr_generator.py` | QrCodeListResponse |
| `server/app/schemas/task.py` | SyncQueueListResponse, TaskListResponse |
| `server/app/schemas/task_intake.py` | TaskIntakeListResponse |
| `server/app/schemas/url.py` | UrlListResponse |
| `server/app/services/admin_users.py` | registry, role, per_page, search, list_users_paginated, ... |
| `server/app/services/data_import.py` | BatchListResult, limit, user, registry, list_batches, ... |
| `server/app/services/feedback.py` | status, registry, sort, list_feedback, page, ... |
| `server/app/services/fileshare.py` | per_page, registry, user_id, list_files, page |
| `server/app/services/health_checker.py` | per_page, created_by, list_by_owner, page |
| `server/app/services/news.py` | list_sources, enabled, per_page, page |
| `server/tests/test_pagination.py` | test_pagination_params_clamps_per_page |

## Connected Communities

- **app/services +11 dirs · delete** (14 cross-edges)
- **app/services +10 dirs · ValidationError** (3 cross-edges)
- **app/services +11 dirs · ApiError** (3 cross-edges)
- **app/services +15 dirs** (3 cross-edges)
- **tests +17 dirs** (2 cross-edges)
- **routers/tools +3 dirs** (2 cross-edges)
- **db/documents +3 dirs** (2 cross-edges)
- **. +3 dirs · list_expenses** (2 cross-edges)
- **app/services +7 dirs · _get_or_create_source_for_url** (2 cross-edges)
- **app/core +4 dirs** (1 cross-edges)
- **app/services +7 dirs · lower** (1 cross-edges)
- **. +4 dirs · select_resume** (1 cross-edges)
- **tests +2 dirs · permission_key** (1 cross-edges)
- **app · patch_permissions** (1 cross-edges)
- **app/services +12 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-409")
explore(operation:"context", task:"understand app/schemas +8 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
