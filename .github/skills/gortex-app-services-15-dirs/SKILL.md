---
name: gortex-app-services-15-dirs
description: "Work in the app/services +15 dirs area — 208 symbols across 49 files (72% cohesion)"
---

# app/services +15 dirs

208 symbols | 49 files | 72% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:app.content.resume_data.RESUME_DATA`
- `external-call::dep:fastapi.responses.PlainTextResponse`
- `external-call::dep:fastapi.responses.Response`
- `external-call::stdlib:tomllib`
- `scripts/generate_docs.py`
- `scripts/update_dependency_versions.py`
- `server/app/core/data_extractor/handlers/json_handler.py`
- `server/app/core/data_extractor/handlers/xml_handler.py`
- `server/app/core/json_lists.py`
- `server/app/core/logging.py`
- `server/app/core/permissions.py`
- `server/app/core/text.py`
- `server/app/core/utils.py`
- `server/app/db/seed/__main__.py`
- `server/app/db/seed/builders/demo.py`
- `server/app/routers/resume.py`
- `server/app/routers/seo.py`
- `server/app/schemas/admin_users.py`
- `server/app/services/fileshare.py`
- `server/app/services/news.py`
- `server/app/services/news_telegram.py`
- `server/app/services/password_generator.py`
- `server/app/services/resume_export.py`
- `server/app/services/search_index.py`
- `server/app/services/search_indexers/news.py`
- `server/app/services/search_indexers/recipe.py`
- `server/app/services/search_indexers/resume.py`
- `server/app/services/search_indexers/task.py`
- `server/app/services/task_intake.py`
- `server/app/services/themealdb.py`
- `server/app/todobot/handlers/start.py`
- `server/app/todobot/handlers/task_create.py`
- `server/app/todobot/handlers/task_manage.py`
- `server/app/todobot/keyboards/expense.py`
- `server/app/todobot/keyboards/task.py`
- `server/app/todobot/utils/expense_nlp.py`
- `server/app/todobot/utils/nlp.py`
- `server/app/todobot/utils/oneshot.py`
- `server/scripts/eval_groq_prompts.py`
- `server/tests/test_email.py`
- `server/tests/test_oneshot.py`
- `server/tests/test_permissions.py`
- `server/tests/test_resume_export.py`
- `server/tests/test_stripe_donations.py`
- `server/tests/test_todobot_ux.py`
- `server/tests/test_tools/test_password_generator.py`
- `server/tests/test_url_safety.py`
- `server/tests/test_utils.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | extend, get, os, upper, ArgumentTypeError, ... |
| `external-call::dep:app.content.resume_data.RESUME_DATA` | app.content.resume_data.RESUME_DATA |
| `external-call::dep:fastapi.responses.PlainTextResponse` | fastapi.responses.PlainTextResponse |
| `external-call::dep:fastapi.responses.Response` | fastapi.responses.Response |
| `external-call::stdlib:tomllib` | tomllib |
| `scripts/generate_docs.py` | _esc_cell, schema, _log, message, _endpoint_rows, ... |
| `scripts/update_dependency_versions.py` | text, collect_python_requirements |
| `server/app/core/data_extractor/handlers/json_handler.py` | _collect_columns, records |
| `server/app/core/data_extractor/handlers/xml_handler.py` | rows, _collect_columns |
| `server/app/core/json_lists.py` | strict, parse_json_string_list, field, raw |
| `server/app/core/logging.py` | _stderr_level |
| `server/app/core/permissions.py` | permissions, all_registry_permissions, validate_permissions |
| `server/app/core/text.py` | text, normalize_whitespace |
| `server/app/core/utils.py` | attachment_content_disposition, filename |
| `server/app/db/seed/__main__.py` | value, _parse_only |
| `server/app/db/seed/builders/demo.py` | seed, build_recipe_tag_pool, count |
| `server/app/routers/resume.py` | get_recruiter_profile, download_resume_json, download_resume_markdown |
| `server/app/routers/seo.py` | _url_entry, registry, loc, robots_txt, _public_paths, ... |
| `server/app/schemas/admin_users.py` | UpdateUserPermissionsRequest, value, check_permissions |
| `server/app/services/fileshare.py` | name, _sanitize_filename |
| `server/app/services/news.py` | handle_data, data |
| `server/app/services/news_telegram.py` | theme, _theme_tag, _escape, value, format_news_telegram_message, ... |
| `server/app/services/password_generator.py` | charset, _apply_ambiguous_filter, exclude_ambiguous, digits, symbols, ... |
| `server/app/services/resume_export.py` | profile_seo_title, selection, selection, resume, projects, ... |
| `server/app/services/search_index.py` | text, _truncate_snippet, build_context_block, results, snippet, ... |
| `server/app/services/search_indexers/news.py` | _news_document, article |
| `server/app/services/search_indexers/recipe.py` | recipe, _recipe_document |
| `server/app/services/search_indexers/resume.py` | _skills_text, _resume_documents, skills |
| `server/app/services/search_indexers/task.py` | _task_document, task |
| `server/app/services/task_intake.py` | build_confirmation_summary, draft |
| `server/app/services/themealdb.py` | build_tags, meal |
| `server/app/todobot/handlers/start.py` | build_welcome_text, calendar_connected, pending_tasks |
| `server/app/todobot/handlers/task_create.py` | data, _format_summary |
| `server/app/todobot/handlers/task_manage.py` | task, _detail_text |
| `server/app/todobot/keyboards/expense.py` | category_picker, category_names |
| `server/app/todobot/keyboards/task.py` | my_task_time_picker, selected_date, task_id, time_picker, selected_date |
| `server/app/todobot/utils/expense_nlp.py` | text, _detect_currency, default |
| `server/app/todobot/utils/nlp.py` | _datetime_tokens, text |
| `server/app/todobot/utils/oneshot.py` | format_month_grid, year, month, tasks, timezone_name |
| `server/scripts/eval_groq_prompts.py` | task, payload, api_key, turns, xml, ... |
| `server/tests/test_email.py` | _message, context, capture_info |
| `server/tests/test_oneshot.py` | test_month_grid_empty_month |
| `server/tests/test_permissions.py` | test_validate_permissions_rejects_unknown |
| `server/tests/test_resume_export.py` | test_build_share_query_is_deterministic, test_recruiter_profile_copy, test_resume_markdown_sections |
| `server/tests/test_stripe_donations.py` | text, text, fake_notify, fake_notify |
| `server/tests/test_todobot_ux.py` | test_build_welcome_text_lists_pending_and_calendar |
| `server/tests/test_tools/test_password_generator.py` | test_password_generator_includes_all_selected_sets, client |
| `server/tests/test_url_safety.py` | func, tracking_to_thread, args, kwargs |
| `server/tests/test_utils.py` | test_attachment_content_disposition_ascii_fallback, test_attachment_content_disposition_utf8_name |

## Entry Points

- `server/scripts/eval_groq_prompts.py::run_eval`

## Connected Communities

- **app/services +12 dirs** (14 cross-edges)
- **. +5 dirs · aiogram.types.InlineKeyboardBut…** (13 cross-edges)
- **app/services +7 dirs · lower** (10 cross-edges)
- **app/services +8 dirs · escape** (10 cross-edges)
- **tests +17 dirs** (9 cross-edges)
- **tests +10 dirs** (9 cross-edges)
- **app/services +7 dirs · upsert** (7 cross-edges)
- **seed/core +7 dirs** (6 cross-edges)
- **. +8 dirs · ingest** (3 cross-edges)
- **app/services +2 dirs · parse_groq_usage** (2 cross-edges)
- **. +1 dirs · _build_mongodb_url** (2 cross-edges)
- **app/services +11 dirs · ApiError** (2 cross-edges)
- **app/services +10 dirs · ValidationError** (2 cross-edges)
- **tests +9 dirs** (2 cross-edges)
- **tests +3 dirs** (1 cross-edges)
- **tests +2 dirs · permission_key** (1 cross-edges)
- **app/services +2 dirs · get_summary** (1 cross-edges)
- **. +8 dirs · app.core.logging.logger** (1 cross-edges)
- **tests +7 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-460")
explore(operation:"context", task:"understand app/services +15 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"server/scripts/eval_groq_prompts.py::run_eval"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
