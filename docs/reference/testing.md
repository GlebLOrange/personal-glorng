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

<!--
ci-ok keep: cursor/ci-ok-path-coverage (78bec9ed) so a pull request path outside the fast gate and the skip allowlist fails ci-ok.
cursor/ai-brand-showcase stays unported because tip 617eef64 is only the agy-ai-tool spec already in docs/specs/agy-ai-tool.md.
cursor/eval-groq-prompts stays unported because the offline eval already lives in server/scripts/eval_groq_prompts.py.
cursor/space-theme stays unported because tip 35d7dbca has no space-theme commit and the atmosphere work was reverted.
cursor/unify-admin-list-rows stays unported because tip 9bf2af40 is not the unify commit and admin rows are already AdminDataRow.
pr-687-tmp stays unported because tip a2c261c4 pins weather while client/e2e/smoke.spec.ts expects weather in the tools catalog.
-->

On pull requests, jobs are path-filtered. Pushes to `main` run backend and frontend. The aggregator **`ci-ok`** succeeds when the `changes` job succeeded, every selected job succeeded, and every changed path is a gate path or on the skip allowlist. Any other path fails `ci-ok`. During development the `main-protection` ruleset is **disabled**, so this check is advisory; require `ci-ok` and `gitleaks` before production ([DevOps checklist](/operations/devops-checklist#development-vs-production-github--cicd)).

Gate paths:

- **backend** — `server/**`, `shared/**`, `rabbitmq/**`, `deploy/**`, `scripts/**`, `nginx/**`, `Makefile`, `docker-compose*.yml`, `.github/workflows/**`, `.env.example`, `.env.production.example`, `.dockerignore`, `.pre-commit-config.yaml`. Runs Ruff check/format, advisory mypy, and `pytest -m "not integration"` with coverage (mongomock + FakeRedis).
- **frontend** — `client/**`, `shared/**`, `nginx/**`, `docker-compose*.yml`, `.github/workflows/**`. Runs `npm run lint` / `format:check`, `test:coverage`, `build:check`, and the Playwright built-shell smoke (`e2e/built-shell.spec.ts`, vite preview, no API).

Skip allowlist (both jobs may be skipped and `ci-ok` can still succeed): `docs/**`, `**/*.md`, `**/*.mdc`, GitHub metadata (issue templates, `FUNDING.yml`, `dependabot.yml`, copilot instructions, social preview), `.cursor/**`, `.devcontainer/**`, `.vscode/**`, `postman/**`, editor dotfiles (`.editorconfig`, `.nvmrc`, `.gitignore`, `.ignore`, `.rgignore`, `.cursorignore`), `.gitleaks.toml`, and `LICENSE`. Gitleaks still runs from [`security.yml`](../../.github/workflows/security.yml) on every pull request.

Manual [`ci-extended.yml`](../../.github/workflows/ci-extended.yml) (`workflow_dispatch`):

- **postgres-tests** — `pytest -m postgres` (Alembic + Postgres service; also marked `integration`)
- **e2e** — Playwright (`client/e2e/*.spec.ts`, smoke + admin-tools) against compose API + preview
- **docs** — `scripts/generate_docs.py` freshness check + VitePress build

### P1 — Nightly

Automated today ([`nightly.yml`](../../.github/workflows/nightly.yml)):

- `pytest -m redis` — real Redis connectivity / round-trip (also marked `integration`)

Postgres integration (`pytest -m postgres`), API Playwright, and docs freshness run in manual [`ci-extended.yml`](../../.github/workflows/ci-extended.yml).

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
cd client && VITE_PUBLIC_ORIGIN=https://ci.example.test npm run build:check && \
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
| Postgres audit/search | Built (manual `ci-extended` `postgres-tests`) | `test_postgres_integration.py` |
| Health / readiness | Built | `test_health.py`, `test_broker_health.py` |
| Sentry init (mock) | Built | `test_sentry_init.py` |
| Feature flags | Built | `test_feature_flags.py` |
| Celery beat registry | Built (P2 unit) | `test_celery_schedule.py`, `test_celery_conf.py` |
| Registry parity | Maintain | `test_platform_parity.py`, `services.parity.test.ts` |
| Portfolio / resume UI | Built | `resumeGlance.test.ts`, E2E smoke |
| Admin UI harness | Built | `adminToolHarness.test.ts` |
| Admin Playwright flows | Built (manual `ci-extended` e2e; PR gate runs built-shell smoke) | `admin-tools.spec.ts` |

## Related

- [Contributing](/guide/contributing)
- [Database — tests](/operations/database#tests)
