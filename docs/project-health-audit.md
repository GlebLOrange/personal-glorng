# Project health audit

Updated: 2026-06-06

Branch: `cursor/project-health-check-29ad`

Audited commit: `cceb54497f9a2adcb8ff17627ed76e13f5d89425` (PR #67, `Cursor/pln expense exchange rates`)

## Scope

This audit covers dependency vulnerabilities, security-sensitive code paths, Docker/Compose deployment posture, logging, CI gates, DRY/maintainability, and obvious reliability/product problems.

## Checks run

- `npm audit --audit-level=high` in `client/`: **0 vulnerabilities**.
- `npm ci` in `client/`: completed, **0 vulnerabilities**; local Node `v22.14.0` produced `EBADENGINE` warnings for Babel 8 RC packages requiring `^22.18.0 || >=24.11.0`.
- `npm run lint && npm run format:check` in `client/`: ESLint has 5 warnings; Prettier fails on 20 files.
- `uv run ruff check . && uv run ruff format --check .` in `server/`: Ruff check fails with 26 errors, 18 fixable. Format check did not run because `ruff check` failed first.
- `uv export --format requirements-txt --no-dev --no-hashes -o /tmp/glorng-requirements-67.txt && uv run --with pip-audit pip-audit -r /tmp/glorng-requirements-67.txt --progress-spinner off` in `server/`: 2 known CVEs in `aiohttp==3.13.5`.
- `gitleaks detect`: not run locally because `gitleaks` is not installed in this VM.
- `docker compose -f docker-compose.prod.yml config`: not run locally because Docker is not installed in this VM.
- Product/unit tests were not run because this was an audit/report task and the user preference says not to run tests unless explicitly asked.

## Highest priority findings

1. **Python dependency CVEs are present via `aiohttp==3.13.5`.**
   - Evidence: `pip-audit` reports `CVE-2026-34993` and `CVE-2026-47265`, both fixed by `aiohttp==3.14.0`.
   - Dependency path: `aiogram==3.28.2` -> `aiohttp==3.13.5` from `server/pyproject.toml`.
   - Recommended task: upgrade `aiogram` if it permits `aiohttp>=3.14`, or add a safe override/constraint and regenerate `server/uv.lock`.

2. **The security workflow likely fails before Python auditing.**
   - `.github/workflows/security.yml:36-41` installs pip-audit with `uv pip install pip-audit` without an explicit venv or `--system`, then runs `uv run pip-audit`.
   - A prior main-branch audit observed this failing in GitHub Actions before dependency audit could run.
   - Recommended task: replace with `uv run --with pip-audit pip-audit -r /tmp/requirements.txt`, `uv tool run pip-audit`, or create/use an explicit venv.

3. **OAuth credentials are stored plaintext in the database.**
   - GitHub: `server/app/db/models/github_credential.py:17-19`, stored in `server/app/routers/github.py:85-108`.
   - Google: `server/app/db/models/google_auth.py:18`, stored in `server/app/routers/callbacks.py:76-84`.
   - GitHub OAuth requests broad `repo` scope at `server/app/routers/github.py:54-58`.
   - Google requests full calendar scope at `server/app/routers/callbacks.py:60`.
   - Recommended task: encrypt tokens at rest or move them to a secret manager; narrow scopes where product behavior allows.

4. **Auth endpoints return JWTs in JSON while also setting HttpOnly cookies.**
   - `server/app/routers/auth.py:96-108` and `server/app/routers/auth.py:121-147` set cookies and return `TokenResponse` with access and refresh tokens.
   - `client/src/composables/useApi.ts` uses credentialed requests and the client does not appear to require storing tokens.
   - Risk: XSS can read login/refresh response bodies even though cookies are HttpOnly.
   - Recommended task: use cookie-only responses for browser flows, or split browser and API-token auth flows.

5. **Telegram bot authorization is disabled by default when a bot token is configured without an allowlist.**
   - Default/example allowed ID is `0` in `server/app/settings.py:90-94` and `.env.example`.
   - Middleware only rejects when the value is truthy: `server/app/todobot/middlewares/auth.py:20-27`.
   - Recommended task: fail fast in production if `TELEGRAM_BOT_TO_DO_TOKEN` is set and `TELEGRAM_ALLOWED_USER_ID` is `0`.

6. **Rate limiting trusts spoofable `X-Forwarded-For`.**
   - `server/app/core/rate_limit.py:23-29` uses the first `x-forwarded-for` value directly.
   - `docker-compose.lite.yml:3-5` exposes the server on `8000:8000`, so direct clients can send spoofed forwarded headers.
   - Recommended task: bind lite API to `127.0.0.1` and only trust forwarded client IPs from known proxy networks.

7. **Production file-share behavior differs from development and backend limits.**
   - Public download route exists at `server/app/routers/tools/fileshare.py:75-95`.
   - Dev nginx proxies `/f/` at `nginx/nginx.conf:59-63`; prod nginx lacks `/f/` in `nginx/nginx.prod.conf:40-58`.
   - Backend allows 100 MB uploads at `server/app/services/fileshare.py:16`; prod nginx `/api` caps body size at 5 MB in `nginx/nginx.prod.conf:40-45`.
   - Recommended task: add prod `/f/` proxying and align prod upload size with the backend limit or lower the backend limit.

8. **Shared files can be served through `/media/` if the stored name is known.**
   - Shared files are stored under `MEDIA_DIR/shares` in `server/app/services/fileshare.py:36-65`.
   - Nginx serves the whole media tree with `/media/` aliases in `nginx/nginx.conf:65-70` and `nginx/nginx.prod.conf:53-58`.
   - Risk: direct `/media/shares/...` access bypasses `/f/{code}` expiry, download counters, and rate limiting.
   - Recommended task: store shared files outside public media or deny `/media/shares/` at nginx.

9. **Email console logging can leak token-bearing verification/reset URLs.**
   - `server/app/core/email.py:21-25` logs the first 200 characters of HTML.
   - Verification/reset renderers include tokens in URLs at `server/app/core/email.py:78-94`.
   - Recommended task: log metadata only; do not log email body previews for auth emails.

10. **CSV export is vulnerable to spreadsheet formula injection.**
    - `server/app/services/tool_expense.py:182-198` writes user-controlled category, product, notes, and source cells directly.
    - Recommended task: escape cells beginning with `=`, `+`, `-`, `@`, tab, or CR before CSV output.

## Quality gate findings

- Backend Ruff check currently fails with 26 errors. Representative issues:
  - `server/app/routers/tools/expenses.py:1` import ordering from the current expense/currency work.
  - `server/app/services/tool_expense.py:114` line length.
  - Multiple Python 3.14 style upgrades such as `Generator[bytes, None, None]` -> `Generator[bytes]`.
- Frontend ESLint has 5 warnings:
  - `client/src/components/ui/BaseImage.vue`: missing default values for optional props.
  - `client/src/pages/admin/DashboardPage.vue`: attribute order warning.
  - `client/src/pages/admin/tools/EmailTool.vue`: `v-html` warning; this is intentionally mitigated by DOMPurify in `client/src/utils/sanitizeEmailHtml.ts`.
- Frontend Prettier fails on 20 files, including the current expense/currency files:
  - `client/src/components/expenses/ExpenseCurrencyConverter.vue`
  - `client/src/pages/admin/tools/ExpensesTool.vue`
  - chart/weather/resume/privacy/router files listed in the command output.

## Logging and observability findings

- Request middleware logs every start and completion at INFO: `server/app/core/middleware.py:56` and `server/app/core/middleware.py:82`. This may be noisy in production.
- Request user correlation is effectively broken for the main browser flow:
  - `server/app/core/middleware.py:15-34` only reads Bearer auth, ignores auth cookies, and tries to parse JWT `sub` as `int`, while auth uses public UUID subjects.
- Auth and feedback logs include raw email addresses:
  - `server/app/routers/auth.py:89`
  - `server/app/routers/auth.py:203-206`
  - `server/app/routers/feedback.py:33-36`
- `server/app/services/github.py:17-26` and `server/app/services/github.py:45-54` create `httpx.AsyncClient()` without explicit timeouts.
- Feedback Telegram notification is fire-and-forget in `server/app/routers/feedback.py:38-47`; failures can be detached from request context.
- Sentry and Loguru both capture exception paths; review duplicate reporting between `server/app/core/logging.py` and exception handlers in `server/app/main.py`.

## DRY and maintainability backlog

- Currency definitions/defaults can drift:
  - Backend literal: `server/app/schemas/tool_expense.py:7`.
  - Backend service tuple: `server/app/services/currency.py:12-16`.
  - Settings default: `server/app/settings.py:95`.
  - Frontend constants live in `client/src/composables/useExpenseFilters.ts`.
  - Add parity tests or generate frontend/backend currency metadata from one source.
- PLN-first behavior is not fully aligned:
  - `EXPENSE_DEFAULT_CURRENCY` is PLN in settings/client, but `ToolExpenseCreate.currency` still defaults to USD at `server/app/schemas/tool_expense.py:35`.
  - Database server default is USD at `server/app/db/models/tool_expense.py:15`.
  - Summary display default is USD at `server/app/services/tool_expense.py:205`.
- Expense UI and other admin tools repeat `console.error(err)` + toast handling:
  - `client/src/pages/admin/tools/ExpensesTool.vue:253-263`, `266-327`, `364-384`, `391-405`.
  - `client/src/components/expenses/ExpenseCurrencyConverter.vue:52-67`.
  - Candidate future task: centralize API action/error handling and suppress raw console noise in production.
- Audit record construction is repeated in domain services such as `ToolExpenseService` and file-share service.
- Transaction ownership is inconsistent: request-level DB dependency commits after handlers, but some routes/services commit/flush internally. Keep one transaction boundary unless a route explicitly needs intermediate persistence.
- Platform/tool metadata is duplicated between backend registry and frontend router permission maps; add a generated or fetched metadata contract when touching platform navigation.

## Docker and deployment findings

- Server Dockerfile uses `COPY --from=ghcr.io/astral-sh/uv:latest`; pin the uv image/digest for reproducible builds.
- Client dev Dockerfile uses `npm install` instead of lockfile-strict `npm ci`.
- No `.dockerignore` files were found, so Docker contexts may include local artifacts if ignore coverage drifts.
- `client/Dockerfile.prod` runs as `appuser` and copies `/dist` into `/usr/share/nginx/html` at runtime. Verify named volume ownership permits this copy in production.
- Production compose exposes only HTTP port 80. If TLS is terminated outside this compose stack, document that explicitly because auth cookies are `secure` in production.
- There is no app-level health/readiness endpoint; Compose checks only infrastructure service health.

## Lower priority hardening

- CSP still allows `'unsafe-inline'` for scripts/styles as documented in `docs/security.md:13`.
- CSRF referer matching in `server/app/core/csrf.py:21-27` requires `referer.startswith(f"{allowed}/")`; an exact allowed-origin referer without a trailing slash would fail.
- Expired shared files are rejected on download but are not proactively cleaned up.
- Video download concurrency checks use private semaphore state in `server/app/routers/tools/viddownload.py`.
- Product copy drift: platform registry mentions Groq for AI chat while implementation uses OpenAI.

## Positive posture to preserve

- Locked frontend/backend dependencies and security CI are present.
- CodeQL/security workflows exist; npm audit is currently clean.
- Production settings reject weak JWT secrets and wildcard CORS with credentials.
- Auth cookies are HttpOnly and secure in production.
- Cookie-auth mutating requests have production CSRF origin checks.
- Redis-backed rate limiting uses an atomic Lua increment/expire.
- Video download uses `asyncio.create_subprocess_exec` rather than `shell=True`, validates YouTube hosts, and restricts format input.
- Email preview uses DOMPurify before `v-html`.
- Sentry is configured with privacy-aware defaults.
- Docker images use Alpine and non-root users.
- Security posture is documented in `docs/security.md` and `SECURITY.md`.

## Suggested future task order

### P0

1. Fix the Python security workflow and make pip-audit run reliably in CI.
2. Resolve the `aiohttp` CVEs by upgrading/overriding dependencies and regenerating `uv.lock`.
3. Fix current Ruff and Prettier drift so CI quality gates are green.
4. Fix production file-share `/f/` routing, upload-size mismatch, and `/media/shares/` bypass.
5. Remove token-bearing email body previews from logs.
6. Harden rate-limit client IP handling and lite compose binding.
7. Enforce Telegram allowlist when the bot token is configured.

### P1

1. Encrypt/vault OAuth tokens and narrow OAuth scopes.
2. Stop returning refresh/access tokens in JSON for browser cookie flows.
3. Escape CSV cells in expense exports.
4. Align or document PLN-first backend defaults.
5. Restore request user correlation for cookie auth and UUID subjects.
6. Add health/readiness endpoints and expired shared-file cleanup.

### P2

1. Consolidate currency/platform metadata contracts.
2. Centralize frontend admin API error/toast handling.
3. Review production logging levels and PII redaction policy.
4. Add container/image scanning and Dependabot coverage for Docker/GitHub Actions.
5. Add Postgres-specific CI coverage for features that SQLite does not exercise.
