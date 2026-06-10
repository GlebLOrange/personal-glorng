# gLOrng Platform

gLOrng is a **personal platform** where the same domain services power the public portfolio, admin panel, Telegram todobot, and Celery background workers.

## Channels

| Channel | Entry | Uses |
|---------|-------|------|
| Public web | `/` | Resume, donations, feedback |
| Admin panel | `/admin` | Platform services via `/api/tools/*` |
| Telegram bot | `app.todobot.main` | Task creation and reminders |
| Worker | `celery -A app.workers.celery_app worker` | Reminders, calendar sync, cleanup |
| Beat | `celery -A app.workers.celery_app beat` | Scheduled cron tasks |

## Service Catalog

Registry source of truth: [`server/app/platform/registry.py`](../server/app/platform/registry.py)

Exposed via `GET /api/platform/services` for the admin dashboard.

Full endpoint reference (public vs admin, capabilities, UI routes): [api-tools.md](api-tools.md).

## Module-as-Service Pattern

```
Router (HTTP/auth) → Service (logic + audit) → MongoDB / Redis (+ optional PostgreSQL for search/audit)
Channel adapter (Vue page, bot handler) → Service
```

## Observability

Two complementary streams:

1. **Operational telemetry** — structured JSON logs (Loguru) + Sentry for debugging and incidents. Not queryable as audit.
2. **Audit trail** — `audit_events` table with `security` and `domain` categories. Reviewable at `/admin/tools/audit`.

Services emit audit events on mutations and auth flows. HTTP middleware correlates `request_id` and `user_id` in logs.

## Related docs

- [API tools](api-tools.md) — public and admin endpoints, capabilities, programmatic access
- [Security](security.md) — CSP, auth, CSRF, sanitization, admin-tool risks
- [Database](database.md) — migrations and test database notes
