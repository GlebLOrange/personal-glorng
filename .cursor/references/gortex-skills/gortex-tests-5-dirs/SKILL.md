---
name: gortex-tests-5-dirs
description: "Work in the tests +5 dirs area — 388 symbols across 51 files (75% cohesion)"
---

# tests +5 dirs

388 symbols | 51 files | 75% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:httpx.ASGITransport`
- `external-call::dep:httpx.AsyncClient`
- `server/app/core/app_log_persist.py`
- `server/app/db/documents/app_log.py`
- `server/app/db/documents/base.py`
- `server/app/db/documents/credential.py`
- `server/app/db/repositories/app_log.py`
- `server/app/db/repositories/credential.py`
- `server/app/services/elasticsearch_app_logs.py`
- `server/tests/conftest.py`
- `server/tests/factories.py`
- `server/tests/test_account.py`
- `server/tests/test_admin_search_api.py`
- `server/tests/test_admin_users.py`
- `server/tests/test_app_log_persist.py`
- `server/tests/test_app_logs_api.py`
- `server/tests/test_audit_mutations.py`
- `server/tests/test_auth.py`
- `server/tests/test_calendar.py`
- `server/tests/test_data_extractor.py`
- `server/tests/test_date_filters.py`
- `server/tests/test_donations.py`
- `server/tests/test_expense_calculator_public.py`
- `server/tests/test_expense_categories.py`
- `server/tests/test_expenses.py`
- `server/tests/test_fake_redis_ttl.py`
- `server/tests/test_feature_flags.py`
- `server/tests/test_feedback.py`
- `server/tests/test_file_share.py`
- `server/tests/test_github_api.py`
- `server/tests/test_health.py`
- `server/tests/test_llm_json.py`
- `server/tests/test_maintenance.py`
- `server/tests/test_middleware_logging.py`
- `server/tests/test_oauth_state.py`
- `server/tests/test_pagination.py`
- `server/tests/test_platform.py`
- `server/tests/test_platform_parity.py`
- `server/tests/test_recipes.py`
- `server/tests/test_refresh.py`
- `server/tests/test_resume.py`
- `server/tests/test_resume_export.py`
- `server/tests/test_resume_pdf.py`
- `server/tests/test_search_index.py`
- `server/tests/test_seo.py`
- `server/tests/test_stripe_donations.py`
- `server/tests/test_task_intake.py`
- `server/tests/test_tasks_admin.py`
- `server/tests/test_weather.py`
- `server/tests/test_world_time.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | pop, sleep, fromisoformat, index |
| `external-call::dep:httpx.ASGITransport` | httpx.ASGITransport |
| `external-call::dep:httpx.AsyncClient` | httpx.AsyncClient |
| `server/app/core/app_log_persist.py` | entry, _entry_to_app_log, entry, _extract_context |
| `server/app/db/documents/app_log.py` | AppLog |
| `server/app/db/documents/base.py` | exclude_none, doc, document_to_dict |
| `server/app/db/documents/credential.py` | GitHubCredential |
| `server/app/db/repositories/app_log.py` | _from_doc, entries, data, insert_many |
| `server/app/db/repositories/credential.py` | cred, upsert_github |
| `server/app/services/elasticsearch_app_logs.py` | source, _hit_to_app_log |
| `server/tests/conftest.py` | value, key, redis, __init__, __init__, ... |
| `server/tests/factories.py` | theme, message, email, registry, status, ... |
| `server/tests/test_account.py` | test_update_profile, test_preferences_round_trip, auth_client, auth_client |
| `server/tests/test_admin_search_api.py` | no_perms_client, auth_client, test_admin_search_requires_capability, test_admin_search_rejects_short_query |
| `server/tests/test_admin_users.py` | db, test_admin_users_stats, test_list_users_search_escapes_regex_metacharacters, admin_user, auth_client, ... |
| `server/tests/test_app_log_persist.py` | registry, test_repository_insert_many |
| `server/tests/test_app_logs_api.py` | auth_client, test_app_logs_filter_by_message_substring, registry, auth_client, registry, ... |
| `server/tests/test_audit_mutations.py` | auth_client, test_url_delete_emits_audit, registry |
| `server/tests/test_auth.py` | auth_client, client, test_me_unauthorized, test_me_authenticated |
| `server/tests/test_calendar.py` | test_rejects_invalid_state, client |
| `server/tests/test_data_extractor.py` | test_list_import_batches, test_get_import_batch_detail, auth_client, auth_client |
| `server/tests/test_date_filters.py` | auth_client, test_audit_reject_inverted_date_range, auth_client, auth_client, test_expenses_reject_invalid_month, ... |
| `server/tests/test_donations.py` | test_donations_config_returns_structure, test_donations_stripe_fields, client, client |
| `server/tests/test_expense_calculator_public.py` | test_rates_unauthenticated, client, client, auth_client, test_state_requires_auth, ... |
| `server/tests/test_expense_categories.py` | test_update_category_budget, auth_client, auth_client, auth_client, test_deleted_starter_does_not_return, ... |
| `server/tests/test_expenses.py` | auth_client, auth_client, client, test_summary_converts_to_display_currency, test_get_exchange_rates, ... |
| `server/tests/test_fake_redis_ttl.py` | test_fake_redis_honours_ttl, test_fake_redis_expire_sets_deadline |
| `server/tests/test_feature_flags.py` | client, tmp_path, monkeypatch, client, test_expenses_api_returns_503_when_disabled, ... |
| `server/tests/test_feedback.py` | registry, registry, TestUpdateFeedbackStatus, registry, auth_client, ... |
| `server/tests/test_file_share.py` | auth_client, test_download_sanitized_content_disposition, auth_client, test_delete_file, test_download_invalid_code_chars, ... |
| `server/tests/test_github_api.py` | admin_user, test_resume_github_cache_miss_returns_empty_repos, test_public_github_repos, client, monkeypatch, ... |
| `server/tests/test_health.py` | client, test_health_returns_ok, client, test_ready_returns_dependency_checks, client, ... |
| `server/tests/test_llm_json.py` | json |
| `server/tests/test_maintenance.py` | auth_client, test_maintenance_requires_auth, client, test_maintenance_status_defaults |
| `server/tests/test_middleware_logging.py` | test_forged_x_request_id_is_ignored, tmp_path, monkeypatch, test_request_completed_log_includes_request_id, tmp_path, ... |
| `server/tests/test_oauth_state.py` | test_github_oauth_rejects_state_mismatch, client, test_google_oauth_rejects_unknown_state, auth_client |
| `server/tests/test_pagination.py` | test_audit_rejects_invalid_per_page, auth_client |
| `server/tests/test_platform.py` | auth_client, client, test_audit_list_sorts_by_occurred_at, client, test_platform_services_catalog, ... |
| `server/tests/test_platform_parity.py` | test_registry_slugs_are_unique, test_registry_api_prefixes_are_unique |
| `server/tests/test_recipes.py` | test_get_recipe, auth_client, admin_user, test_delete_recipe, registry, ... |
| `server/tests/test_refresh.py` | test_new_access_token_works, client, login_tokens |
| `server/tests/test_resume.py` | test_resume_has_required_fields, client, test_resume_links, test_resume_skills_structure, client, ... |
| `server/tests/test_resume_export.py` | client, test_resume_markdown_download, client, test_resume_profile_endpoint, client, ... |
| `server/tests/test_resume_pdf.py` | client, test_resume_pdf_download, fake_get_cached_resume_pdf, _resume, monkeypatch |
| `server/tests/test_search_index.py` | test_public_search_query, client, auth_client |
| `server/tests/test_seo.py` | client, registry, test_sitemap_xml, test_robots_txt, client, ... |
| `server/tests/test_stripe_donations.py` | client, test_donations_config_includes_checkout_flag |
| `server/tests/test_task_intake.py` | auth_client, test_list_intakes_admin |
| `server/tests/test_tasks_admin.py` | registry, auth_client, auth_client, auth_client, test_create_task, ... |
| `server/tests/test_weather.py` | client, auth_client, auth_client, client, test_weather_location_cannot_delete_default, ... |
| `server/tests/test_world_time.py` | test_lookup_world_time_endpoint, client |

## Connected Communities

- **tests +3 dirs** (38 cross-edges)
- **tests +17 dirs** (16 cross-edges)
- **tests +7 dirs** (11 cross-edges)
- **tests +10 dirs** (11 cross-edges)
- **app/services +7 dirs · lower** (8 cross-edges)
- **app/services +15 dirs** (4 cross-edges)
- **. +3 dirs · _drain_queue** (4 cross-edges)
- **. +4 dirs · download_video** (3 cross-edges)
- **app/services +8 dirs · record** (3 cross-edges)
- **app/db · utc_now** (2 cross-edges)
- **. +3 dirs · decrypt_secret** (2 cross-edges)
- **app/services +10 dirs · create_article** (2 cross-edges)
- **tests +6 dirs · create_user** (2 cross-edges)
- **app/services +12 dirs** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **seed/core +7 dirs** (1 cross-edges)
- **tests · _audit_action** (1 cross-edges)
- **app/routers +3 dirs** (1 cross-edges)
- **db/repositories +4 dirs** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-512")
explore(operation:"context", task:"understand tests +5 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
