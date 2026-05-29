# Learning & improvement roadmap

Personal platform repo: FastAPI + Vue 3 + PostgreSQL + Redis + ARQ + Telegram bot.

**How to use:** Pick one item per sprint. Prefer **Tier A** (close gaps) before **Tier B** (incremental upgrades) unless exploring is the goal. Mark items `[x]` when done, `[~]` in progress, `[-]` skipped.

**Related docs:** [docs/platform.md](docs/platform.md) (channels, observability model) · [docs/database.md](docs/database.md) (migrations, Postgres test gap)

---

## Recommended first five

1. `[x]` **Quality CI** — [`.github/workflows/ci.yml`](.github/workflows/ci.yml): ruff, pytest, client lint/test/build, Alembic check, Playwright smoke
2. `[x]` **pre-commit** — [`.pre-commit-config.yaml`](.pre-commit-config.yaml): ruff, client eslint/prettier/typecheck, gitleaks (`pip install pre-commit && pre-commit install`)
3. `[~]` **Vitest** — composable tests added; optional follow-up: [`ExpensesTool.vue`](client/src/pages/admin/tools/ExpensesTool.vue) component test
4. `[ ]` **Instructor** — smallest LLM refactor vs adopting LangChain ← **next**
5. `[ ]` **Postgres integration tests** — closes blind spot for recipe FTS and PG-only features

---

## Already in place

Do not re-build these; extend or integrate with them instead.

| Area | What exists |
|------|-------------|
| Task queue | ARQ workers — [`server/app/workers/`](server/app/workers/) |
| Observability | Structured JSON logs (Loguru), Sentry — [`server/app/main.py`](server/app/main.py), [`client/src/instrument.ts`](client/src/instrument.ts) |
| Audit trail | `audit_events` + `/admin/tools/audit` — see [docs/platform.md](docs/platform.md) |
| Backend tests | 33 test files under [`server/tests/`](server/tests/) |
| Local quality | `make test`, `make lint` — [`Makefile`](Makefile), [`server/pyproject.toml`](server/pyproject.toml) |
| Security CI | gitleaks, pip-audit, npm audit — [`.github/workflows/security.yml`](.github/workflows/security.yml) |
| Quality CI | ruff, pytest, frontend lint/test/build, db check, Playwright — [`.github/workflows/ci.yml`](.github/workflows/ci.yml) |
| Git hooks | pre-commit (ruff + client lint/format/typecheck) — [`.pre-commit-config.yaml`](.pre-commit-config.yaml) |
| Frontend tests | Vitest — `client/src/**/*.test.ts` (composables, stores, utils) |
| Dependency updates | Dependabot weekly — [`.github/dependabot.yml`](.github/dependabot.yml) |
| Rate limiting | Atomic Redis Lua (`INCR` + `EXPIRE`) — [`server/app/core/rate_limit.py`](server/app/core/rate_limit.py) |

---

## Tier A — Close gaps in the current stack

Highest ROI; directly tied to repo pain points.

### CI and hooks

- `[x]` **Quality CI** — [`.github/workflows/ci.yml`](.github/workflows/ci.yml); local mirror: `make check` (set `CHECK_DB=0` to skip db-check)
  - [`Makefile`](Makefile)

- `[x]` **pre-commit** — [`.pre-commit-config.yaml`](.pre-commit-config.yaml) includes client `typecheck` (`vue-tsc -b`)

### Frontend tests

- `[~]` **Vitest + Vue Test Utils** — Composable coverage done; component test for expenses page still optional.
  - [`client/src/composables/useExpenseFilters.test.ts`](client/src/composables/useExpenseFilters.test.ts)
  - [`client/src/composables/useCachedApi.test.ts`](client/src/composables/useCachedApi.test.ts)
  - [`client/src/pages/admin/tools/ExpensesTool.vue`](client/src/pages/admin/tools/ExpensesTool.vue) (optional next)

### Backend test coverage gaps

- `[ ]` **Postgres integration tests** — Default pytest uses SQLite; GIN full-text search and other PG features are not exercised. Add optional `pytest` marker + compose profile for recipe search and migration-sensitive paths.
  - [docs/database.md](docs/database.md) (Tests section)
  - [`server/tests/conftest.py`](server/tests/conftest.py)
  - [`server/app/db/recipe_search.py`](server/app/db/recipe_search.py)

- `[ ]` **Hypothesis** — Property-based tests for NLP parsers where edge cases are hard to enumerate manually.
  - [`server/app/todobot/utils/nlp.py`](server/app/todobot/utils/nlp.py) (`parse_task_input`)
  - [`server/app/todobot/utils/expense_nlp.py`](server/app/todobot/utils/expense_nlp.py) (`parse_expense_text`)
  - [`server/tests/test_nlp.py`](server/tests/test_nlp.py), [`server/tests/test_expense_nlp.py`](server/tests/test_expense_nlp.py)

### Load testing

- `[ ]` **locust** — Load-test rate limits and hot API paths under concurrency. Lua script is already atomic; value is validation and capacity planning, not fixing a race.
  - [`server/app/core/rate_limit.py`](server/app/core/rate_limit.py)
  - [`server/tests/test_rate_limit_lua.py`](server/tests/test_rate_limit_lua.py)

---

## Tier B — Incremental upgrades

Improve what you built without replacing the whole stack.

### LLM / NLP

- `[ ]` **Instructor** — Structured LLM outputs via Pydantic; cleaner than `complete_json`. Prefer over LangChain/LlamaIndex for this codebase size.
  - [`server/app/services/llm_json.py`](server/app/services/llm_json.py)
  - [`server/app/services/task_intake.py`](server/app/services/task_intake.py)

- `[ ]` **Anthropic Claude API** — Compare with OpenAI for tool use and structured output (educational; OpenAI is wired today).
  - [`server/app/services/ai_chat.py`](server/app/services/ai_chat.py)

### Frontend

- `[ ]` **Pinia Colada** — Replace hand-rolled cached fetching; vue-router 5 lists it as an optional peer dependency.
  - [`client/src/composables/useCachedApi.ts`](client/src/composables/useCachedApi.ts)
  - `client/package-lock.json` (optional peer `@pinia/colada`)

- `[ ]` **VueUse** — Replace custom composables and manual click-outside handling.
  - [`client/src/composables/useClipboard.ts`](client/src/composables/useClipboard.ts)
  - [`client/src/composables/useWeatherCity.ts`](client/src/composables/useWeatherCity.ts)
  - [`client/src/components/weather/WeatherCard.vue`](client/src/components/weather/WeatherCard.vue)

- `[ ]` **Storybook** — Document UI kit in isolation.
  - [`client/src/components/ui/BaseCard.vue`](client/src/components/ui/BaseCard.vue)
  - [`client/src/components/ui/BaseButton.vue`](client/src/components/ui/BaseButton.vue)
  - [`client/src/components/ui/BaseInput.vue`](client/src/components/ui/BaseInput.vue)
  - [`client/src/components/ui/BaseModal.vue`](client/src/components/ui/BaseModal.vue)
  - [`client/src/components/ui/BaseTextarea.vue`](client/src/components/ui/BaseTextarea.vue)

- `[ ]` **TanStack Table** — Headless table for sorting, pagination, filtering on the expenses grid.
  - [`client/src/pages/admin/tools/ExpensesTool.vue`](client/src/pages/admin/tools/ExpensesTool.vue)

### Observability

- `[ ]` **OpenTelemetry** — Complement Loguru + Sentry with distributed traces (API → ARQ worker → Telegram bot); do not replace structured logging.
  - [`docs/platform.md`](docs/platform.md)
  - [`server/app/main.py`](server/app/main.py)

- `[ ]` **Prometheus + Grafana** — `/metrics` via prometheus-fastapi-instrumentator; dashboards for task queue, sync failures, expense totals.
  - [`server/app/workers/tasks.py`](server/app/workers/tasks.py)

- `[ ]` **Loki** — Ship structured JSON logs into Grafana for querying alongside metrics.

### Database and storage

- `[ ]` **Alembic autogenerate review** — Write migrations by hand first, compare with autogenerate; manual wins for ENUM/bootstrap cases.
  - [`server/app/db/migrations/versions/c4e8f2a91b3d_add_todobot_tables.py`](server/app/db/migrations/versions/c4e8f2a91b3d_add_todobot_tables.py)
  - [docs/database.md](docs/database.md)

- `[ ]` **MinIO** — S3-compatible storage instead of local disk for file share.
  - [`server/app/services/fileshare.py`](server/app/services/fileshare.py)
  - [`server/app/settings.py`](server/app/settings.py) (`MEDIA_DIR`, default `/app/media`)

- `[ ]` **pgAdmin or TablePlus** — GUI for indexes, explain plans, schema inspection (host port `5433` in dev per [docs/database.md](docs/database.md)).

- `[ ]` **Redis Insight** — Inspect rate-limit keys, token blacklist, weather cache in real time.

### Dependencies

- `[x]` **uv** — Lockfile and faster installs; `server/uv.lock`, Docker `uv sync --frozen`, CI via `astral-sh/setup-uv`.
  - [`server/pyproject.toml`](server/pyproject.toml)
  - [`server/Dockerfile`](server/Dockerfile)

### Frontend polish (performance & accessibility)

- `[x]` **Performance & accessibility polish** — DevTools-driven LCP/a11y fixes, self-hosted fonts, Tailwind v4 `@utility` patterns.
  - [`client/src/styles/main.css`](client/src/styles/main.css)
  - [`client/src/pages/PortfolioPage.vue`](client/src/pages/PortfolioPage.vue)

## Performance & accessibility baselines

Audited with Chrome DevTools (production `vite build` + `vite preview`, Mobile throttling) on `/` and `/admin/tools/calculator` after login. Re-run locally after changes.

| Route | Metric | Before (pre-change) | After (target) |
|-------|--------|---------------------|----------------|
| `/` | LCP | ~3.5–4.5s (hero blocked on `/api/resume` + Google Fonts) | &lt;2.5s (static hero + self-hosted fonts) |
| `/` | CLS | ~0.05–0.15 (full-page swap after load) | &lt;0.1 (hero stable on first paint) |
| `/` | INP | &lt;200ms (few interactions on load) | &lt;200ms |
| `/` | A11y | Nav missing label; no skip link; focus rings on `:focus` | Landmarks + skip link + `:focus-visible` |
| `/admin/tools/calculator` | A11y | Display not announced; operator labels implicit | `aria-live` on display |

**Before issues (fixed):** portfolio gated on API; external font CSS; decorative section prefix without screen-reader handling; calculator display not in live region.

**How to re-measure:** `cd client && npm run build && npm run preview`, open DevTools → Performance (LCP, CLS, INP) and Accessibility panels.

### Platform-specific (built features)

- `[ ]` **Jira sync (phase 2)** — Model stub exists; dual-write with Calendar sync queue when ready.
  - [`server/app/db/models/jira_sync_queue.py`](server/app/db/models/jira_sync_queue.py)
  - [`server/app/db/models/task.py`](server/app/db/models/task.py) (`jira_issue_key`)

---

## Tier C — Exploratory / compare-and-contrast

Learning goals; pick one topic per exploration sprint. ARQ/nginx/Postgres FTS are sufficient at current scale.

### Task queues and workflows

- `[ ]` **Celery** — Compare with ARQ; Flower dashboard for visibility. [`server/app/workers/pool.py`](server/app/workers/pool.py)
- `[ ]` **Dramatiq** — Middle ground between ARQ and Celery complexity.
- `[ ]` **FastStream** — Event-driven messaging (Kafka/RabbitMQ); natural follow-on after ARQ.
- `[ ]` **Temporal** — Durable workflows vs manual retry in worker tasks (`Retry(defer=60 * job_try)`, `MAX_JOB_TRIES = 3`).
  - [`server/app/workers/tasks.py`](server/app/workers/tasks.py)
  - [`server/app/db/models/google_sync_queue.py`](server/app/db/models/google_sync_queue.py)

### Telegram bot

- `[ ]` **aiogram-dialog** — Widget system for complex FSM; could simplify large handler modules.
  - [`server/app/todobot/handlers/task_create.py`](server/app/todobot/handlers/task_create.py)

### Search and API styles

- `[ ]` **Typesense or Meilisearch** — Dedicated search vs PostgreSQL FTS.
  - [`server/app/db/recipe_search.py`](server/app/db/recipe_search.py)
  - [`server/app/services/recipe.py`](server/app/services/recipe.py)

- `[ ]` **Strawberry GraphQL** — GraphQL alongside REST; schema design practice.
- `[ ]` **SQLModel** — FastAPI author’s merge of SQLAlchemy + Pydantic; compare with separate [`server/app/db/models/`](server/app/db/models/) + [`server/app/schemas/`](server/app/schemas/).
- `[ ]` **Litestar** — Alternative ASGI framework; understand what FastAPI abstracts.

### Infrastructure

- `[ ]` **Traefik** — Automatic HTTPS and dynamic routing vs nginx (high migration cost; nginx is wired in [`nginx/`](nginx/) and prod compose).
- `[ ]` **Coolify or Dokku** — Self-hosted PaaS over Docker Compose.

### Database (if curious)

- `[ ]` **TimescaleDB** — Time-series for expenses/tasks; only if you want analytics beyond current charts.
- `[ ]` **pgBadger** — PostgreSQL query log analysis once tables have real volume.

### AI (if curious)

- `[ ]` **LangChain or LlamaIndex** — Broader abstractions; study what to adopt vs avoid given manual prompts in task intake.
  - [`server/app/services/task_intake.py`](server/app/services/task_intake.py)
- `[ ]` **Weights & Biases** — Experiment tracking for `TASK_INTAKE_CONFIDENCE_THRESHOLD` tuning (heavy for a single env var; consider only if expanding NLP experiments).
  - [`server/app/settings.py`](server/app/settings.py)
  - [`.env.example`](.env.example)
