---
name: gortex-tests-3-dirs
description: "Work in the tests +3 dirs area — 345 symbols across 32 files (73% cohesion)"
---

# tests +3 dirs

345 symbols | 32 files | 73% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `server/app/core/security.py`
- `server/tests/test_account.py`
- `server/tests/test_audit_extended.py`
- `server/tests/test_auth.py`
- `server/tests/test_csrf_middleware.py`
- `server/tests/test_currency.py`
- `server/tests/test_data_extractor.py`
- `server/tests/test_date_filters.py`
- `server/tests/test_email.py`
- `server/tests/test_expense_calculator_public.py`
- `server/tests/test_expenses.py`
- `server/tests/test_feedback.py`
- `server/tests/test_file_share.py`
- `server/tests/test_llm_json.py`
- `server/tests/test_oauth_state.py`
- `server/tests/test_platform.py`
- `server/tests/test_rate_limit.py`
- `server/tests/test_recipes.py`
- `server/tests/test_refresh.py`
- `server/tests/test_stripe_donations.py`
- `server/tests/test_tasks_admin.py`
- `server/tests/test_tool_permissions.py`
- `server/tests/test_tools/test_ai_chat.py`
- `server/tests/test_tools/test_calculator.py`
- `server/tests/test_tools/test_health_checker.py`
- `server/tests/test_tools/test_password_generator.py`
- `server/tests/test_tools/test_qr_generator.py`
- `server/tests/test_tools/test_urlshortener.py`
- `server/tests/test_viddownload.py`
- `server/tests/test_weather.py`
- `server/tests/test_webhooks.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | io.BytesIO, parse_qs, intersection, encode, urllib.parse.parse_qs, ... |
| `server/app/core/security.py` | create_reset_token, email |
| `server/tests/test_account.py` | test_change_password_revokes_old_token, client, test_change_password_wrong_current, db, auth_client, ... |
| `server/tests/test_audit_extended.py` | test_audit_api_is_read_only, auth_client |
| `server/tests/test_auth.py` | client, test_login_verified, client, client, test_verify_reuse_prevented, ... |
| `server/tests/test_csrf_middleware.py` | client, test_csrf_rejects_cookie_refresh_without_origin, monkeypatch |
| `server/tests/test_currency.py` | client, test_expense_convert, auth_client, test_expense_convert_requires_auth |
| `server/tests/test_data_extractor.py` | auth_client, test_extract_api_csv, auth_client, auth_client, test_import_api_csv, ... |
| `server/tests/test_date_filters.py` | test_create_task_rejects_invalid_scheduled_at, auth_client |
| `server/tests/test_email.py` | auth_client, auth_client, test_email_preview_escapes_html, test_email_preview_unauthorized, auth_client, ... |
| `server/tests/test_expense_calculator_public.py` | test_convert_invalid_amount, test_convert_unauthenticated, client, client |
| `server/tests/test_expenses.py` | auth_client, auth_client, test_summary_month_param, auth_client, test_summary_aggregation, ... |
| `server/tests/test_feedback.py` | test_create_feedback_invalid_email, test_create_feedback, client, test_create_feedback_sanitizes_theme_and_message, client, ... |
| `server/tests/test_file_share.py` | monkeypatch, test_upload_file, auth_client, auth_client, name, ... |
| `server/tests/test_llm_json.py` | post, url, kwargs |
| `server/tests/test_oauth_state.py` | fake_exchange_code_for_token, registry, fake_get_github_user, auth_client, monkeypatch, ... |
| `server/tests/test_platform.py` | admin_user, test_login_emits_security_audit, registry, client |
| `server/tests/test_rate_limit.py` | TestFeedbackRateLimit, client, client, test_allows_within_limit, test_blocks_over_limit |
| `server/tests/test_recipes.py` | auth_client, test_update_empty_ingredients, auth_client, TestRecipesList, test_create_rejects_too_many_tags, ... |
| `server/tests/test_refresh.py` | client, login_tokens, login_tokens, client, login_tokens, ... |
| `server/tests/test_stripe_donations.py` | test_stripe_webhook_rejects_invalid_signature, test_stripe_webhook_deduplicates_replay, client, payload, client, ... |
| `server/tests/test_tasks_admin.py` | test_create_task_truncates_long_description, test_create_task_rejects_empty_title_after_sanitize, test_create_task_sanitizes_description_and_location, auth_client, auth_client, ... |
| `server/tests/test_tool_permissions.py` | test_admin_tools_require_capabilities, no_perms_client, path, method |
| `server/tests/test_tools/test_ai_chat.py` | auth_client, groq_chat_service, auth_client, test_ai_chat_unauthenticated, test_ai_chat_rejects_empty_content, ... |
| `server/tests/test_tools/test_calculator.py` | auth_client, auth_client, test_calculator_multiply, test_calculator_divide, auth_client, ... |
| `server/tests/test_tools/test_health_checker.py` | test_create_monitor_rejects_private_url, auth_client |
| `server/tests/test_tools/test_password_generator.py` | test_password_generator_length_out_of_range, client, client, client, test_password_generator_custom_length, ... |
| `server/tests/test_tools/test_qr_generator.py` | client, test_qr_generator_rejects_empty_content, auth_client, test_qr_library_empty_patch_rejected |
| `server/tests/test_tools/test_urlshortener.py` | auth_client, auth_client, auth_client, test_create_url_invalid_url, test_create_url_unauthenticated, ... |
| `server/tests/test_viddownload.py` | auth_client, test_viddownload_requires_auth, test_viddownload_rejects_invalid_format, auth_client, test_viddownload_rejects_private_host, ... |
| `server/tests/test_weather.py` | test_weather_location_mutations_unauthorized, client, auth_client, test_weather_location_invalid_query, auth_client, ... |
| `server/tests/test_webhooks.py` | client, test_webhook_unknown_slug, client, test_webhook_rejects_oversized_body, client, ... |

## Connected Communities

- **tests +5 dirs** (87 cross-edges)
- **app/services +7 dirs · lower** (8 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **tests +6 dirs · create_user** (5 cross-edges)
- **app/core +4 dirs** (4 cross-edges)
- **tests +17 dirs** (2 cross-edges)
- **seed/core +7 dirs** (2 cross-edges)
- **app/core** (1 cross-edges)
- **app/services +10 dirs · create_article** (1 cross-edges)
- **app/services +8 dirs · record** (1 cross-edges)
- **tests +10 dirs** (1 cross-edges)
- **. +8 dirs · app.core.logging.logger** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-509")
explore(operation:"context", task:"understand tests +3 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
