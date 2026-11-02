---
name: gortex-tests-10-dirs-get-settings
description: "Work in the tests +10 dirs · get_settings area — 255 symbols across 44 files (74% cohesion)"
---

# tests +10 dirs · get_settings

255 symbols | 44 files | 74% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `external-call::dep:app.platform.registry.CATEGORY_LABELS`
- `external-call::dep:fastapi.FastAPI`
- `external-call::dep:pydantic_settings.sources.DotEnvSettingsSource`
- `external-call::stdlib:pytest`
- `server/app/core/csrf.py`
- `server/app/core/deps.py`
- `server/app/core/feature_flags.py`
- `server/app/core/mongodb.py`
- `server/app/db/deps.py`
- `server/app/db/registry.py`
- `server/app/main.py`
- `server/app/openapi.py`
- `server/app/routers/__init__.py`
- `server/app/routers/auth.py`
- `server/app/routers/donations.py`
- `server/app/routers/health.py`
- `server/app/routers/platform.py`
- `server/app/routers/tools/ai_chat.py`
- `server/app/routers/tools/urlshortener.py`
- `server/app/schemas/donations.py`
- `server/app/schemas/platform.py`
- `server/app/services/github_credentials.py`
- `server/app/services/maintenance.py`
- `server/app/settings.py`
- `server/app/workers/celery_app.py`
- `server/tests/conftest.py`
- `server/tests/env_helpers.py`
- `server/tests/test_auth_cookies.py`
- `server/tests/test_csrf.py`
- `server/tests/test_data_extractor.py`
- `server/tests/test_feature_flags.py`
- `server/tests/test_fernet_secrets.py`
- `server/tests/test_github_api.py`
- `server/tests/test_maintenance.py`
- `server/tests/test_mongodb.py`
- `server/tests/test_redis_settings.py`
- `server/tests/test_schemas_validators.py`
- `server/tests/test_search_index.py`
- `server/tests/test_sentry_init.py`
- `server/tests/test_settings.py`
- `server/tests/test_stripe_donations.py`
- `server/tests/test_tools/test_ai_chat.py`
- `server/tests/test_webhooks.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | Path, title, pathlib.Path |
| `external-call::dep:app.platform.registry.CATEGORY_LABELS` | app.platform.registry.CATEGORY_LABELS |
| `external-call::dep:fastapi.FastAPI` | fastapi.FastAPI |
| `external-call::dep:pydantic_settings.sources.DotEnvSettingsSource` | pydantic_settings.sources.DotEnvSettingsSource |
| `external-call::stdlib:pytest` | pytest |
| `server/app/core/csrf.py` | allowed_origins, request, _origin_allowed, request, csrf_origin_rejected |
| `server/app/core/deps.py` | registry, settings, _optional_postgres_session |
| `server/app/core/feature_flags.py` | is_service_enabled, is_ai_chat_enabled, is_expenses_enabled, is_ai_search_enabled, slug, ... |
| `server/app/core/mongodb.py` | get_mongodb_client |
| `server/app/db/deps.py` | get_postgres_db, registry, settings |
| `server/app/db/registry.py` | require_postgres_factory |
| `server/app/main.py` | _init_sentry, create_app |
| `server/app/openapi.py` | app, configure_openapi |
| `server/app/routers/__init__.py` | api_router |
| `server/app/routers/auth.py` | _set_auth_cookies, settings, response, settings, access_token, ... |
| `server/app/routers/donations.py` | get_donations_config |
| `server/app/routers/health.py` | settings, settings, request, _check_postgres, settings, ... |
| `server/app/routers/platform.py` | _platform_catalog, list_platform_services, platform_catalog |
| `server/app/routers/tools/ai_chat.py` | settings |
| `server/app/routers/tools/urlshortener.py` | redirect_router |
| `server/app/schemas/donations.py` | StripeDonationConfig, DonationLinkConfig, DonationsConfigResponse |
| `server/app/schemas/platform.py` | PlatformCatalogResponse, PlatformServiceResponse |
| `server/app/services/github_credentials.py` | plaintext, read_github_access_token, stored, store_github_access_token |
| `server/app/services/maintenance.py` | settings |
| `server/app/settings.py` | load_settings_from, dotenv_settings, enable_mongodb, stripe_checkout_enabled, env_settings, ... |
| `server/app/workers/celery_app.py` | _init_worker_sentry, _on_worker_init, _kwargs |
| `server/tests/conftest.py` | tmp_path, _reset_settings_env, temp_media_dir, monkeypatch |
| `server/tests/env_helpers.py` | base, scenario_env, overrides, monkeypatch, env_file, ... |
| `server/tests/test_auth_cookies.py` | test_cookie_secure_in_production, test_cookie_secure_on_https_base_url_in_development, test_cookie_not_secure_on_local_http_dev, test_cookie_secure_in_staging_even_on_http |
| `server/tests/test_csrf.py` | _enable_production, _build_request, path, headers, monkeypatch, ... |
| `server/tests/test_data_extractor.py` | test_extract_xml_rejects_entity_after_padding, test_extract_xml_rejects_dtd, test_extract_invalid_json, test_extract_bytes_without_filename_or_format, test_extract_unknown_extension_without_format, ... |
| `server/tests/test_feature_flags.py` | monkeypatch, test_ai_search_requires_flag_and_api_key, monkeypatch, test_expenses_disabled_by_default_flag, test_untrusted_tools_omitted_from_catalog_when_disabled, ... |
| `server/tests/test_fernet_secrets.py` | test_github_credential_helpers, monkeypatch, test_github_credential_reads_jwt_secret_ciphertext, monkeypatch |
| `server/tests/test_github_api.py` | monkeypatch, github_public_env |
| `server/tests/test_maintenance.py` | auth_client, maintenance_env, tmp_path, monkeypatch, tmp_path, ... |
| `server/tests/test_mongodb.py` | tmp_path, monkeypatch, test_resolve_mongodb_url_maps_compose_host_to_localhost, monkeypatch, test_mongodb_client_kwargs_defaults, ... |
| `server/tests/test_redis_settings.py` | test_shared_redis_cache_warns_in_staging, test_resolve_redis_cache_url_maps_compose_host_to_localhost, tmp_path, tmp_path, caplog, ... |
| `server/tests/test_schemas_validators.py` | test_validate_clean_required_rejects_blank |
| `server/tests/test_search_index.py` | monkeypatch, enable_ai_search |
| `server/tests/test_sentry_init.py` | expected, sentry_enabled_flag, tmp_path, app_env, test_sentry_enabled_matrix, ... |
| `server/tests/test_settings.py` | tmp_path, test_staging_requires_strong_jwt_secret, tmp_path, test_production_requires_strong_postgres_password, test_staging_requires_distinct_fernet_secret, ... |
| `server/tests/test_stripe_donations.py` | monkeypatch, stripe_env |
| `server/tests/test_tools/test_ai_chat.py` | test_ai_chat_disabled_when_flag_off, enable_ai_chat, monkeypatch, tmp_path, monkeypatch, ... |
| `server/tests/test_webhooks.py` | monkeypatch, webhook_env |

## Connected Communities

- **app/services +7 dirs · lower** (16 cross-edges)
- **app/services +12 dirs** (7 cross-edges)
- **routers/tools +10 dirs** (6 cross-edges)
- **app/services +15 dirs** (5 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **. +3 dirs · decrypt_secret** (3 cross-edges)
- **. +1 dirs · api_error_handler** (3 cross-edges)
- **. +8 dirs · app.core.logging.logger** (3 cross-edges)
- **tests +5 dirs** (2 cross-edges)
- **app/schemas +8 dirs** (2 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **tests +3 dirs** (1 cross-edges)
- **. +2 dirs · custom_openapi** (1 cross-edges)
- **app/services +11 dirs · record_domain** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)
- **app/schemas +2 dirs · validate_clean_required** (1 cross-edges)
- **. +2 dirs · _request_with_headers** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-503")
explore(operation:"context", task:"understand tests +10 dirs · get_settings", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
