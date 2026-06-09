# Testing strategy (gLOrng)

Tests are organized into four tiers by CI cost and release risk.

## Tier matrix

| Tier | When | Runtime target | Automation |
|------|------|----------------|------------|
| **P0 — PR gate** | Every pull request | Backend &lt; 5 min, frontend &lt; 3 min | [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) |
| **P1 — Nightly** | `main` branch nightly | &lt; 15 min | [`.github/workflows/nightly.yml`](../.github/workflows/nightly.yml) |
| **P2 — Pre-release** | Before production deploy | &lt; 45 min | [`.github/workflows/pre-release.yml`](../.github/workflows/pre-release.yml) |
| **P3 — Staging manual** | Post-deploy validation | Human-driven | Checklist below |

### P0 — PR gate (default)

- `uv run pytest -m "not integration"` — mongomock + FakeRedis (~375 cases)
- `npm run test` — Vitest unit/component tests
- `npm run lint` / `npm run build`
- Playwright smoke (`client/e2e/smoke.spec.ts`)
- Ruff check/format

### P1 — Nightly

- `pytest -m postgres` — audit/search Postgres dual-write paths (requires migrations)
- `pytest -m redis` — real Redis rate-limit and health checks
- Expanded admin Playwright flows (`admin-tools.spec.ts`)

### P2 — Pre-release

- Docker Compose `worker` profile smoke (one Celery task round-trip)
- Nginx compose profile health (`:80/api/health`)
- `make reindex-search` smoke
- Beat schedule registry unit tests (cron definitions, not live firing)

### P3 — Staging manual (deferred from CI)

These are intentionally **not** automated in CI — flaky, vendor-dependent, or require live credentials:

- **Beat schedule firing** — verify cron tasks run on schedule in staging (not in CI)
- **RabbitMQ dead-letter queue** — only if DLQ is configured in broker policy
- **Telegram bot E2E** — `app/todobot/` has no CI container; validate via staging bot
- **Live Sentry** — trigger one deliberate 500 in staging; confirm issue in Sentry UI
- **Stripe live mode** — use test mode in CI; live keys only in staging manual

## Pytest markers

Defined in [`server/pyproject.toml`](../server/pyproject.toml):

| Marker | Purpose |
|--------|---------|
| `postgres` | Requires `POSTGRES_TEST_URL` and Alembic migrations |
| `redis` | Requires reachable `REDIS_URL` (real instance, not FakeRedis) |
| `integration` | Slow multi-service tests (excluded from P0 default job) |
| `e2e_api` | Full HTTP pipeline including middleware |

## Running tests locally

```bash
# Backend (CI-style, fast)
cd server && uv run pytest -m "not integration" -v

# Postgres integration
POSTGRES_TEST_URL=postgresql+asyncpg://glorng:pass@127.0.0.1:5433/glorng \
  ENABLE_POSTGRES=true DATABASE_URL=$POSTGRES_TEST_URL \
  uv run pytest -m postgres -v

# Redis integration (with local Redis)
REDIS_URL=redis://:local@127.0.0.1:6379/0 uv run pytest -m redis -v

# Frontend
cd client && npm run test

# E2E (API must be up)
cd client && npm run build && \
  VITE_API_PROXY_TARGET=http://127.0.0.1:8000 npm run preview &
npm run e2e
```

## Coverage map (maintain vs build)

| Area | Status | Primary tests |
|------|--------|---------------|
| Auth (login, refresh, verify) | Maintain | `test_auth.py`, `test_refresh.py` |
| Reset password happy path | Built | `test_auth.py` |
| Admin tool APIs | Maintain | `server/tests/test_tools/`, per-tool modules |
| Tool permission matrix | Built | `test_tool_permissions.py` |
| CSRF middleware HTTP | Built | `test_csrf_middleware.py` |
| Middleware → app log | Built | `test_middleware_logging.py` |
| App logs API | Built + maintain | `test_app_logs_api.py` (level, message, request_id, date, pagination) |
| Audit trail | Built + maintain | `test_platform.py`, `test_audit_extended.py`, `test_audit_mutations.py` |
| Postgres audit/search | Built (P1) | `test_postgres_integration.py` |
| Health / readiness | Built | `test_health.py`, `test_broker_health.py` |
| Sentry init (mock) | Built | `test_sentry_init.py` |
| Feature flags | Built | `test_feature_flags.py` |
| Celery beat registry | Built (P2 unit) | `test_celery_schedule.py` |
| Registry parity | Maintain | `test_platform_parity.py`, `services.parity.test.ts` |
| Portfolio / resume UI | Built | `resumeGlance.test.ts`, E2E smoke |
| Admin UI harness | Built | `adminToolHarness.test.ts` |
| Admin Playwright flows | Built (P1) | `admin-tools.spec.ts` |
