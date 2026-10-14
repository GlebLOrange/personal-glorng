# Platform overview

Gleb.Y is a **personal platform** where the same domain services power the public portfolio, admin panel, Telegram todobot, and Celery background workers.

Channels, data stores, and the module-as-service pattern: [Architecture](/guide/architecture).

## Service catalog

Registry source of truth: [`server/app/platform/registry.py`](../../server/app/platform/registry.py)

Exposed via `GET /api/platform/services` for the admin dashboard.

Full endpoint reference (public vs admin, capabilities, UI routes): [API & tools](/reference/api-tools).

## Platform pillars

| Pillar | Services |
|--------|----------|
| **Productivity** | Tasks, Email, Expenses |
| **Content** | Recipes, File share, URL shortener |
| **Utilities** | Calculator, Video download, AI chat |
| **Operations** | Feedback, Audit log |

## Observability

Two complementary streams:

1. **Operational telemetry** — structured JSON logs (Loguru) + Sentry for debugging and incidents. Not queryable as audit.
2. **Audit trail** — `audit_events` table with `security` and `domain` categories. Reviewable at `/admin/audit-logs`.

Services emit audit events on mutations and auth flows. HTTP middleware correlates `request_id` and `user_id` in logs.

## Terminology

- **Platform tool** — a catalogued feature (slug in `registry.py`, e.g. `expenses`, `tasks`).
- **Expense `tool_name`** — vendor or product label on a spending row (e.g. Cursor, groceries); unrelated to platform-tool slugs.

## Related docs

- [Architecture](/guide/architecture) — channels, stores, request pipeline, module-as-service
- [Telegram + tasks + calendar sync](/guide/telegram-tasks-calendar) — todobot, outbox, Google Calendar
- [API & tools](/reference/api-tools) — public and admin endpoints, capabilities, programmatic access
- [Security](/reference/security) — CSP, auth, CSRF, sanitization, admin-tool risks
- [Database](/operations/database) — migrations and test database notes
