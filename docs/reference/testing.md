# Testing

Tests are organized into four tiers by CI cost and release risk.

## Tier matrix

| Tier | When | Runtime target / hard timeout | Automation |
|------|------|-------------------------------|------------|
| **P0 — PR gate** | Every pull request (path-filtered jobs) | Soft targets: backend ~5 min, frontend ~3–8 min; job timeouts in [`ci.yml`](../../.github/workflows/ci.yml) | [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) — aggregator **`ci-ok`** (merge-required only after production ruleset is enabled; see [DevOps checklist](/operations/devops-checklist#development-vs-production-github--cicd)) |
| **P1 — Nightly** | Schedule `0 3 * * *` UTC + `workflow_dispatch` | &lt; 15 min (`timeout-minutes: 15`) | [`.github/workflows/nightly.yml`](../../.github/workflows/nightly.yml) |
| **P2 — Pre-release** | Before production deploy (`workflow_dispatch`) | &lt; 45 min (stack-smoke timeout 30) | [`.github/workflows/pre-release.yml`](../../.github/workflows/pre-release.yml) |
| **P3 — Staging manual** | Post-deploy validation | Human-driven | Checklist below |

Related security automation (not a test tier): [`.github/workflows/security.yml`](../../.github/workflows/security.yml) runs **gitleaks** on every PR/push; **pip-audit** / **npm audit** on schedule, manual dispatch, or when lockfiles change.

### P0 — PR gate (default)

Jobs are path-filtered on pull requests; pushes to `main` run the full suite. Aggregator job `ci-ok` fails if any selected job failed. During development the `main-protection` ruleset is **disabled**, so CI is advisory; enable required checks before production ([DevOps checklist](/operations/devops-checklist#development-vs-production-github--cicd)).

- **backend** — Ruff check/format, mypy, `pytest -m "not integration"` with coverage (mongomock + FakeRedis)
- **frontend** — `npm run lint` / `format:check`, `test:coverage`, `build:check`
- **postgres-tests** — `pytest -m postgres` (Alembic + Postgres service; also marked `integration`)
- **e2e** — Playwright (`client/e2e/*.spec.ts`, smoke + admin-tools) against compose API + preview
- **docs** — `scripts/generate_docs.py` freshness check + VitePress build

### P1 — Nightly

Automated today ([`nightly.yml`](../../.github/workflows/nightly.yml)):

- `pytest -m redis` — real Redis connectivity / round-trip (also marked `integration`)

Postgres integration (`pytest -m postgres`) runs on every PR via the CI `postgres-tests` job, not nightly.

### P2 — Pre-release

Automated today ([`pre-release.yml`](../../.github/workflows/pre-release.yml)):

- Celery unit tests (`tests/test_celery_schedule.py`, `tests/test_celery_conf.py`)
- Compose stack smoke: migrate + API `:8000/api/health` + `/api/ready` (asserts `"mongodb":"ok"`)
- Nginx (dev-lite overlay) `:80/api/health` through the reverse proxy

Not yet in pre-release CI (manual / follow-up):

- Docker Compose `worker` profile smoke (one Celery task round-trip)
- `make reindex-search` smoke

### P3 — Staging manual (deferred from CI) {#p3-staging-manual-deferred-from-ci}

These are intentionally **not** automated in CI — flaky, vendor-dependent, or require live credentials:

- **Beat schedule firing** — verify cron tasks run on schedule in staging (not in CI)
- **RabbitMQ dead-letter queue** — inspect `celery.dlq` after a deliberate poison task; see [Deployment](/operations/deployment#celery-dead-letter-queue)
- **Telegram bot E2E** — `app/todobot/` has no CI container; validate via staging bot
- **Live Sentry** — trigger one deliberate 500 in staging; confirm issue in Sentry UI
- **Stripe live mode** — use test mode in CI; live keys only in staging manual

## Pytest markers

Defined in [`server/pyproject.toml`](../../server/pyproject.toml):

| Marker | Purpose |
|--------|---------|
| `postgres` | Requires `POSTGRES_TEST_URL` and Alembic migrations |
| `redis` | Requires reachable `REDIS_URL` (real instance, not FakeRedis) |
| `integration` | Slow multi-service / real-infra tests (excluded from P0 default job) |
| `e2e_api` | Full HTTP pipeline including middleware |

Postgres and Redis integration modules carry both their specific marker and `integration`, so `-m "not integration"` keeps them out of the P0 gate.

## Coverage

- **Backend:** `pytest-cov` with `[tool.coverage.*]` in `server/pyproject.toml` (`fail_under = 65` on `app`, omitting todobot/migrations/seed). P0 CI passes `--cov=app`.
- **Frontend:** Vitest `@vitest/coverage-v8` gates statements on well-tested paths (`components/ui`, `composables`, `utils`, `stores`, `platform`) with `statements: 25` in `client/vitest.config.ts`. P0 CI runs `npm run test:coverage`.

Line coverage is a regression floor, not a substitute for the feature coverage map below.

## Running tests locally

```bash
# Backend (CI-style, fast)
cd server && uv run pytest -m "not integration" -v --cov=app --cov-report=term-missing:skip-covered

# Postgres integration
POSTGRES_TEST_URL=postgresql+asyncpg://glorng:pass@127.0.0.1:5433/glorng \
  ENABLE_POSTGRES=true DATABASE_URL=$POSTGRES_TEST_URL \
  uv run pytest -m postgres -v

# Redis integration (with local Redis)
REDIS_URL=redis://:local@127.0.0.1:6379/0 uv run pytest -m redis -v

# Frontend
cd client && npm run test:coverage

# E2E (API must be up)
cd client && npm run build:check && \
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
| Postgres audit/search | Built (P0 CI `postgres-tests`) | `test_postgres_integration.py` |
| Health / readiness | Built | `test_health.py`, `test_broker_health.py` |
| Sentry init (mock) | Built | `test_sentry_init.py` |
| Feature flags | Built | `test_feature_flags.py` |
| Celery beat registry | Built (P2 unit) | `test_celery_schedule.py`, `test_celery_conf.py` |
| Registry parity | Maintain | `test_platform_parity.py`, `services.parity.test.ts` |
| Portfolio / resume UI | Built | `resumeGlance.test.ts`, E2E smoke |
| Admin UI harness | Built | `adminToolHarness.test.ts` |
| Admin Playwright flows | Built (P0 E2E) | `admin-tools.spec.ts` |

## Related

- [Contributing](/guide/contributing)
- [Database — tests](/operations/database#tests)
