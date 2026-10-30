---
name: gortex-tests-6-dirs-create-user
description: "Work in the tests +6 dirs · create_user area — 150 symbols across 28 files (66% cohesion)"
---

# tests +6 dirs · create_user

150 symbols | 28 files | 66% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:app.core.request_context.request_id_var`
- `external-call::dep:app.core.request_context.user_id_var`
- `external-call::dep:starlette.responses.JSONResponse`
- `server/app/core/middleware.py`
- `server/app/core/security.py`
- `server/app/db/seed/core/admin.py`
- `server/app/db/seed/demo/users.py`
- `server/app/services/user.py`
- `server/tests/conftest.py`
- `server/tests/factories.py`
- `server/tests/test_account.py`
- `server/tests/test_admin_search_api.py`
- `server/tests/test_admin_users.py`
- `server/tests/test_auth.py`
- `server/tests/test_csrf_middleware.py`
- `server/tests/test_data_extractor.py`
- `server/tests/test_expense_calculator_public.py`
- `server/tests/test_file_share.py`
- `server/tests/test_maintenance.py`
- `server/tests/test_middleware_logging.py`
- `server/tests/test_tasks_admin.py`
- `server/tests/test_tool_permissions.py`
- `server/tests/test_tools/test_ai_chat.py`
- `server/tests/test_tools/test_health_checker.py`
- `server/tests/test_tools/test_qr_generator.py`
- `server/tests/test_tools/test_urlshortener.py`
- `server/tests/test_weather.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | count |
| `external-call::dep:app.core.request_context.request_id_var` | app.core.request_context.request_id_var |
| `external-call::dep:app.core.request_context.user_id_var` | app.core.request_context.user_id_var |
| `external-call::dep:starlette.responses.JSONResponse` | starlette.responses.JSONResponse |
| `server/app/core/middleware.py` | request, content_type, call_next, _sanitize_body_for_log, raw, ... |
| `server/app/core/security.py` | subject, expires_delta, create_access_token, user_id, session_version |
| `server/app/db/seed/core/admin.py` | registry, seed_admin, settings |
| `server/app/db/seed/demo/users.py` | registry, password, seed_demo_users, settings, email, ... |
| `server/app/services/user.py` | email, display_name, permissions, timezone, is_verified, ... |
| `server/tests/conftest.py` | admin_token, admin_user, registry, admin_user |
| `server/tests/factories.py` | is_verified, email, create_user, registry, password, ... |
| `server/tests/test_account.py` | client, test_delete_regular_user, admin_user, db, client, ... |
| `server/tests/test_admin_search_api.py` | registry, no_perms_client, client |
| `server/tests/test_admin_users.py` | db, db, db, auth_client, auth_client, ... |
| `server/tests/test_auth.py` | registry, registry, test_login_unverified, client, client, ... |
| `server/tests/test_csrf_middleware.py` | registry, test_csrf_allows_cookie_post_with_allowed_origin, _enable_production, monkeypatch, client, ... |
| `server/tests/test_data_extractor.py` | test_import_batch_ownership_denied, client, registry |
| `server/tests/test_expense_calculator_public.py` | test_state_requires_superuser, client, registry |
| `server/tests/test_file_share.py` | test_delete_file_other_user_forbidden, registry, auth_client |
| `server/tests/test_maintenance.py` | client, db, test_maintenance_requires_superuser |
| `server/tests/test_middleware_logging.py` | test_body_log_redacts_api_key_fields, test_body_log_redacts_nested_list_secrets, body, _Req, __init__, ... |
| `server/tests/test_tasks_admin.py` | registry, client, tasks_reader_client |
| `server/tests/test_tool_permissions.py` | no_perms_client, registry, client |
| `server/tests/test_tools/test_ai_chat.py` | client, registry, limited_auth_client |
| `server/tests/test_tools/test_health_checker.py` | test_capability_required, registry, client |
| `server/tests/test_tools/test_qr_generator.py` | registry, test_qr_library_forbidden_for_other_user, registry, auth_client, auth_client, ... |
| `server/tests/test_tools/test_urlshortener.py` | client, admin_user, client, test_update_other_users_url_forbidden, registry, ... |
| `server/tests/test_weather.py` | client, registry, test_weather_location_delete_other_user_forbidden |

## Entry Points

- `server/app/core/middleware.py::RequestIdMiddleware.dispatch`

## Connected Communities

- **tests +5 dirs** (23 cross-edges)
- **tests +3 dirs** (16 cross-edges)
- **tests +10 dirs** (8 cross-edges)
- **app/services +7 dirs · lower** (8 cross-edges)
- **. +8 dirs · app.core.logging.logger** (6 cross-edges)
- **app/services +8 dirs · record** (4 cross-edges)
- **tests +7 dirs** (4 cross-edges)
- **app/core +7 dirs** (3 cross-edges)
- **app/services +15 dirs** (2 cross-edges)
- **seed/core +7 dirs** (2 cross-edges)
- **app/services +11 dirs · delete** (2 cross-edges)
- **tests +2 dirs · permission_key** (2 cross-edges)
- **app/core** (2 cross-edges)
- **app/services +12 dirs** (1 cross-edges)
- **tests +17 dirs** (1 cross-edges)
- **app/services +10 dirs · ValidationError** (1 cross-edges)
- **. +2 dirs · _request_with_headers** (1 cross-edges)
- **app/core +1 dirs · decode_token** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-496")
explore(operation:"context", task:"understand tests +6 dirs · create_user", format:"gcx")
relations(operation:"usages", target:{symbol:"server/app/core/middleware.py::RequestIdMiddleware.dispatch"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
