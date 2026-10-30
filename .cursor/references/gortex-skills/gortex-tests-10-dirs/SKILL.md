---
name: gortex-tests-10-dirs
description: "Work in the tests +10 dirs area — 255 symbols across 44 files (74% cohesion)"
---

# tests +10 dirs

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
| `` | pathlib.Path, Path, title |
| `external-call::dep:app.platform.registry.CATEGORY_LABELS` | app.platform.registry.CATEGORY_LABELS |
| `external-call::dep:fastapi.FastAPI` | fastapi.FastAPI |
| `external-call::dep:pydantic_settings.sources.DotEnvSettingsSource` | pydantic_settings.sources.DotEnvSettingsSource |
| `external-call::stdlib:pytest` | pytest |
| `server/app/core/csrf.py` | csrf_origin_rejected, request, _origin_allowed, allowed_origins, request |
| `server/app/core/deps.py` | _optional_postgres_session, settings, registry |
| `server/app/core/feature_flags.py` | is_expenses_enabled, is_untrusted_url_tools_enabled, is_ai_chat_enabled, is_service_enabled, is_ai_search_enabled, ... |
| `server/app/core/mongodb.py` | get_mongodb_client |
| `server/app/db/deps.py` | registry, get_postgres_db, settings |
| `server/app/db/registry.py` | require_postgres_factory |
| `server/app/main.py` | create_app, _init_sentry |
| `server/app/openapi.py` | app, configure_openapi |
| `server/app/routers/__init__.py` | api_router |
| `server/app/routers/auth.py` | access_token, _set_auth_cookies, _CookieFlags, _cookie_flags, refresh_token, ... |
| `server/app/routers/donations.py` | get_donations_config |
| `server/app/routers/health.py` | settings, settings, _check_mongodb, _check_postgres, ready, ... |
| `server/app/routers/platform.py` | platform_catalog, _platform_catalog, list_platform_services |
| `server/app/routers/tools/ai_chat.py` | settings |
| `server/app/routers/tools/urlshortener.py` | redirect_router |
| `server/app/schemas/donations.py` | DonationLinkConfig, DonationsConfigResponse, StripeDonationConfig |
| `server/app/schemas/platform.py` | PlatformServiceResponse, PlatformCatalogResponse |
| `server/app/services/github_credentials.py` | read_github_access_token, plaintext, stored, store_github_access_token |
| `server/app/services/maintenance.py` | settings |
| `server/app/settings.py` | app_log_es_enabled, _resolve_elasticsearch_url, dotenv_settings, url, env_file, ... |
| `server/app/workers/celery_app.py` | _kwargs, _on_worker_init, _init_worker_sentry |
| `server/tests/conftest.py` | monkeypatch, tmp_path, _reset_settings_env, temp_media_dir |
| `server/tests/env_helpers.py` | monkeypatch, tmp_path, overrides, base, activate_env_file, ... |
| `server/tests/test_auth_cookies.py` | test_cookie_secure_in_production, test_cookie_not_secure_on_local_http_dev, test_cookie_secure_in_staging_even_on_http, test_cookie_secure_on_https_base_url_in_development |
| `server/tests/test_csrf.py` | cookies, monkeypatch, headers, method, monkeypatch, ... |
| `server/tests/test_data_extractor.py` | test_extract_xml_rejects_entity_after_padding, test_extract_invalid_xml, test_extract_invalid_json, test_extract_bytes_without_filename_or_format, test_extract_xml_rejects_dtd, ... |
| `server/tests/test_feature_flags.py` | monkeypatch, test_postgres_mirror_requires_both_flags, tmp_path, test_ai_search_enabled_with_key, monkeypatch, ... |
| `server/tests/test_fernet_secrets.py` | monkeypatch, test_github_credential_reads_jwt_secret_ciphertext, test_github_credential_helpers, monkeypatch |
| `server/tests/test_github_api.py` | github_public_env, monkeypatch |
| `server/tests/test_maintenance.py` | monkeypatch, tmp_path, maintenance_env, monkeypatch, test_run_seed_blocked_in_production, ... |
| `server/tests/test_mongodb.py` | test_mongodb_client_kwargs_defaults, tmp_path, tmp_path, monkeypatch, monkeypatch, ... |
| `server/tests/test_redis_settings.py` | test_shared_redis_cache_warns_in_staging, monkeypatch, test_resolve_redis_cache_url_maps_compose_host_to_localhost, tmp_path, monkeypatch, ... |
| `server/tests/test_schemas_validators.py` | test_validate_clean_required_rejects_blank |
| `server/tests/test_search_index.py` | enable_ai_search, monkeypatch |
| `server/tests/test_sentry_init.py` | test_sentry_disabled_without_dsn, base_name, sentry_enabled_flag, test_sentry_enabled_matrix, tmp_path, ... |
| `server/tests/test_settings.py` | tmp_path, test_staging_requires_strong_jwt_secret, tmp_path, test_settings_loads_when_groq_api_key_absent, monkeypatch, ... |
| `server/tests/test_stripe_donations.py` | stripe_env, monkeypatch |
| `server/tests/test_tools/test_ai_chat.py` | enable_ai_chat, monkeypatch, test_ai_chat_config_returns_custom_groq_base_url, test_ai_chat_disabled_when_flag_off, tmp_path, ... |
| `server/tests/test_webhooks.py` | webhook_env, monkeypatch |

## Connected Communities

- **app/services +7 dirs · lower** (16 cross-edges)
- **app/services +12 dirs** (7 cross-edges)
- **app/services +10 dirs · ValidationError** (6 cross-edges)
- **tests +7 dirs** (5 cross-edges)
- **app/services +15 dirs** (5 cross-edges)
- **. +1 dirs · api_error_handler** (3 cross-edges)
- **. +8 dirs · app.core.logging.logger** (3 cross-edges)
- **. +3 dirs · decrypt_secret** (3 cross-edges)
- **tests +5 dirs** (2 cross-edges)
- **app/schemas +8 dirs** (2 cross-edges)
- **app/schemas +2 dirs · validate_clean_required** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)
- **. +3 dirs · list_expenses** (1 cross-edges)
- **. +2 dirs · _request_with_headers** (1 cross-edges)
- **tests +3 dirs** (1 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **. +2 dirs · custom_openapi** (1 cross-edges)
- **app/services +11 dirs · delete** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-506")
explore(operation:"context", task:"understand tests +10 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
