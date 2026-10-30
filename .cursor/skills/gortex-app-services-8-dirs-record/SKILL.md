---
name: gortex-app-services-8-dirs-record
description: "Work in the app/services +8 dirs · record area — 163 symbols across 20 files (67% cohesion)"
---

# app/services +8 dirs · record

163 symbols | 20 files | 67% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `server/app/core/security.py`
- `server/app/db/documents/audit.py`
- `server/app/db/models/audit_event.py`
- `server/app/db/repositories/audit.py`
- `server/app/routers/account.py`
- `server/app/routers/auth.py`
- `server/app/routers/feedback.py`
- `server/app/schemas/auth.py`
- `server/app/schemas/feedback.py`
- `server/app/services/account.py`
- `server/app/services/audit.py`
- `server/app/services/auth.py`
- `server/app/services/user.py`
- `server/app/services/webhooks.py`
- `server/tests/test_audit_extended.py`
- `server/tests/test_audit_helpers.py`
- `server/tests/test_auth.py`
- `server/tests/test_platform.py`
- `server/tests/test_postgres_integration.py`

## Key Files

| File | Symbols |
|------|---------|
| `` | keys |
| `server/app/core/security.py` | email, password, hash_password, create_verification_token, verify_password, ... |
| `server/app/db/documents/audit.py` | AuditSource, AuditActorType, AuditEvent, AuditCategory |
| `server/app/db/models/audit_event.py` | AuditEvent |
| `server/app/db/repositories/audit.py` | _from_doc, list_recent, _fetch_items, record, limit, ... |
| `server/app/routers/account.py` | user, user, patch_me, user, data, ... |
| `server/app/routers/auth.py` | response, data, settings, audit_svc, verify, ... |
| `server/app/routers/feedback.py` | registry, user, data, update_feedback_status, feedback_id |
| `server/app/schemas/auth.py` | VerifyEmailRequest, UserPreferencesResponse, UserResponse |
| `server/app/schemas/feedback.py` | FeedbackStatusUpdate |
| `server/app/services/account.py` | user, update_preferences, updates, new_password, change_password, ... |
| `server/app/services/audit.py` | resource_id, list_events, source, sort, actor_type, ... |
| `server/app/services/auth.py` | registry, token, login_user, password, audit, ... |
| `server/app/services/user.py` | default_user_permissions, email, registry, get_user_by_email |
| `server/app/services/webhooks.py` | dispatch_webhook, slug, payload, registry |
| `server/tests/test_audit_extended.py` | test_audit_filter_by_actor_and_resource, auth_client, test_audit_list_uses_mongo_when_postgres_mirror_fails, registry, actor_id, ... |
| `server/tests/test_audit_helpers.py` | test_domain_event_builds_domain_record |
| `server/tests/test_auth.py` | registry, client, test_register_disabled |
| `server/tests/test_platform.py` | registry, registry, test_audit_service_records_event, auth_client, test_audit_list_admin |
| `server/tests/test_postgres_integration.py` | postgres_session, test_audit_dual_write_postgres, monkeypatch, registry |

## Connected Communities

- **app/services +11 dirs · delete** (17 cross-edges)
- **tests +5 dirs** (13 cross-edges)
- **app/core +7 dirs** (8 cross-edges)
- **app/services +7 dirs · lower** (6 cross-edges)
- **tests +17 dirs** (6 cross-edges)
- **. +8 dirs · app.core.logging.logger** (6 cross-edges)
- **tests +6 dirs · create_user** (5 cross-edges)
- **app/services +12 dirs** (4 cross-edges)
- **tests +10 dirs** (4 cross-edges)
- **app/services +10 dirs · create_article** (2 cross-edges)
- **tests +3 dirs** (2 cross-edges)
- **app/core** (2 cross-edges)
- **app · MessageResponse** (2 cross-edges)
- **. +12 dirs** (1 cross-edges)
- **app/services +8 dirs · escape** (1 cross-edges)
- **app/services +15 dirs** (1 cross-edges)
- **app/core +4 dirs** (1 cross-edges)
- **app/services +7 dirs · upsert** (1 cross-edges)
- **app/services +11 dirs · ApiError** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-436")
explore(operation:"context", task:"understand app/services +8 dirs · record", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
