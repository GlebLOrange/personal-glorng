# Project health audit

Updated: 2026-06-06
Branch: `cursor/project-health-check-95d7`
Audited commit: `aa1f3e89082bc7868a15d0f124587a77fa3a21cb`
Context: after PR #66, "Embed currency converter in expenses with PLN-first rates"

This is a saved health, security, DRY, logging, and operations snapshot for future
maintenance tasks. It is an audit report only; no product code was changed.

## Stack summary

- Backend: FastAPI, SQLAlchemy async, Redis, ARQ workers, aiogram Telegram bot.
- Frontend: Vue 3, Vite, TypeScript, Pinia, Vitest, Playwright.
- Infra: nginx, Docker Compose, PostgreSQL, Redis, GitHub Actions, CodeQL,
  Dependabot, gitleaks, pip-audit, npm audit.
- Dependency managers: `uv` for Python, `npm` for frontend.

## Checks run in this audit

- `git status --short --branch`
- `git log --oneline --decorate -5`
- `gh pr view 66 --json state,mergedAt,mergeCommit,headRefName,baseRefName,title,url`
- `gh run list --branch main --limit 15`
- `gh run view 27075797735 --log-failed`
- `npm audit --audit-level=high`
- `npm ci`
- `npm run lint && npm run format:check`
- `uv export --format requirements-txt --no-dev --no-hashes -o /tmp/glorng-requirements.txt`
- `uv run --with pip-audit pip-audit -r /tmp/glorng-requirements.txt`
- `uv run ruff check .`
- `uv run ruff format --check .`
- Targeted source scans for TODO/FIXME markers, subprocess/shell/eval patterns,
  sensitive logging, localStorage, `v-html`, and currency defaults.

Product tests were not run because this was an audit/report task and the saved
user preference says not to run tests unless explicitly asked.

## Current tool results

### Security workflows

- Latest main security workflow for PR #66 merge failed:
  `security` run `27075797735`.
- Failure cause: `.github/workflows/security.yml` runs
  `uv pip install pip-audit` without creating a virtual environment or using
  `--system`; GitHub Actions exits with:
  `No virtual environment found for Python 3.14`.
- Latest main CodeQL workflow succeeded for the same commit.

### Dependency audits

- Frontend: `npm audit --audit-level=high` found 0 vulnerabilities.
- `npm ci` found 0 vulnerabilities, but emitted local environment warnings:
  Babel 8 RC packages require Node `^22.18.0 || >=24.11.0`, while this machine
  has Node `v22.14.0`. It also warned that transitive `glob@10.5.0` is
  deprecated.
- Backend: `pip-audit` found 2 known vulnerabilities in `aiohttp==3.13.5`:
  - `CVE-2026-34993`, fixed in `aiohttp==3.14.0`
  - `CVE-2026-47265`, fixed in `aiohttp==3.14.0`
- `aiohttp` is pulled through `aiogram==3.28.2`.

### Quality gates

- Backend Ruff lint failed with 25 errors, 18 fixable. Representative files:
  - `server/app/routers/tools/expenses.py`: unsorted imports introduced by PR #66
  - `server/app/services/tool_expense.py`: line length
  - `server/app/core/security.py`: line length
  - `server/app/todobot/main.py`: import order and line length
  - `server/tests/conftest.py`: Python 3.14 typing modernization
  - `server/tests/test_oauth_state.py`: line length
  - `server/tests/test_weather.py`: line length
- Backend Ruff format check failed: 14 files would be reformatted.
- Frontend ESLint passed with 5 warnings:
  - `client/src/components/ui/BaseImage.vue`: optional props need defaults
  - `client/src/pages/admin/DashboardPage.vue`: Vue attribute order
  - `client/src/pages/admin/tools/EmailTool.vue`: `v-html` warning; sanitizer is
    used and the code has a local disable comment
- Frontend Prettier check failed: 18 files would be formatted. PR #66 added
  `client/src/components/expenses/ExpenseCurrencyConverter.vue` to the drift.

## Priority findings

### P0 - Fix soon

1. **Security workflow is broken before dependency audit runs.**
   - Location: `.github/workflows/security.yml:36-41`
   - Current command `uv pip install pip-audit` fails on GitHub Actions because
     no venv exists for Python 3.14.
   - Recommendation: replace with `uv run --with pip-audit pip-audit ...`,
     `uv tool run pip-audit ...`, create `uv venv`, or use `uv pip install
     --system`.

2. **Known Python dependency CVEs in `aiohttp==3.13.5`.**
   - Location: `server/uv.lock`, dependency path through `aiogram==3.28.2`.
   - `pip-audit` reports two CVEs fixed by `aiohttp==3.14.0`.
   - Recommendation: upgrade/override `aiohttp` to 3.14.0+ and validate Telegram
     bot behavior.

3. **CI quality gates are currently red locally.**
   - Backend Ruff lint and format fail.
   - Frontend Prettier fails.
   - Recommendation: run `ruff check --fix`, `ruff format`, and Prettier in
     focused cleanup PRs, then verify CI.

4. **Production file-share downloads are probably broken.**
   - Dev nginx has `/f/`: `nginx/nginx.conf:59-63`.
   - Prod nginx lacks `/f/`: `nginx/nginx.prod.conf`.
   - Public links like `/f/{code}` can fall through to the SPA instead of
     FastAPI.
   - Recommendation: add a prod `/f/` proxy block mirroring dev.

5. **Production upload size limit conflicts with backend file-share limit.**
   - Backend max: `server/app/services/fileshare.py:16` is 100 MB.
   - Dev nginx: `nginx/nginx.conf:46-50` uses `client_max_body_size 100m`.
   - Prod nginx: `nginx/nginx.prod.conf:40-44` uses `client_max_body_size 5m`.
   - Recommendation: align prod nginx with backend, or deliberately lower the
     backend limit and docs.

6. **Shared files are stored under publicly served media.**
   - File-share disk path: `server/app/services/fileshare.py:36-65` stores under
     `MEDIA_DIR/shares`.
   - Prod nginx serves all `/media/`: `nginx/nginx.prod.conf:53-58`.
   - This can bypass `/f/{code}` expiry, download counters, and rate limiting if
     a stored filename is known.
   - Recommendation: store shares outside the public media alias or block
     `/media/shares/` at nginx.

7. **Console email backend logs token-bearing HTML previews.**
   - Location: `server/app/core/email.py:21-25`.
   - Verification/reset links include tokens in rendered HTML
     (`server/app/core/email.py:78-95`).
   - Recommendation: log metadata only; never include HTML previews containing
     tokens.

8. **Rate limiting trusts spoofable `X-Forwarded-For`.**
   - Location: `server/app/core/rate_limit.py:23-29`.
   - If the API is exposed directly in dev-lite or through a proxy that appends
     client-supplied XFF, clients can rotate the first IP and bypass buckets.
   - Recommendation: trust forwarded headers only behind known proxies; prefer
     trusted `X-Real-IP` or proxy middleware configured by environment.

9. **Telegram allowlist is disabled by default.**
   - Location: `server/app/settings.py:90-94`.
   - `TELEGRAM_ALLOWED_USER_ID=0` means no user restriction if a bot token is
     configured.
   - Recommendation: fail fast in production when Telegram bot tokens are set
     but no non-zero allowlist is configured.

### P1 - Security and observability hardening

10. **OAuth tokens are stored plaintext in PostgreSQL.**
    - GitHub: `server/app/db/models/github_credential.py:17-19`
    - Google: `server/app/db/models/google_auth.py:13-18`
    - Recommendation: add application-level encryption or vault/KMS backed token
      storage and rotate existing tokens.

11. **Production secret validation only checks `JWT_SECRET`.**
    - Location: `server/app/settings.py:39-52`.
    - Redis/Postgres/SMTP/OpenAI/GitHub/Google secrets are not checked for weak
      placeholder markers.
    - Recommendation: extend production validation for required secrets and
      placeholder markers.

12. **Request log user correlation is broken for normal auth.**
    - Location: `server/app/core/middleware.py:15-34`.
    - JWT `sub` is a UUID public id, but middleware tries `int(sub)`. Cookie auth
      is also ignored, so request logs often miss user context.
    - Recommendation: parse UUID public id or attach user context after auth
      dependency resolution.

13. **Per-request INFO logs can be noisy.**
    - Location: `server/app/core/middleware.py:56,82`.
    - Every request logs start and completion at INFO.
    - Recommendation: add log-level/config controls and consider one structured
      completion log per request.

14. **Sensitive PII appears in auth logs and audit metadata.**
    - Location: `server/app/services/auth.py:77,120,215`.
    - Email logging is useful for auth audit, but should be reviewed for PII
      policy and retention.

15. **CSP still allows inline scripts and styles.**
    - Location: `nginx/security_headers.conf:4-5`.
    - This is documented as a tradeoff, but remains a hardening gap.
    - Recommendation: move production builds toward nonce/hash based CSP.

16. **CSRF referer exact-origin edge case.**
    - Location: `server/app/core/csrf.py:21-26`.
    - `Referer: https://example.com` without trailing slash does not match even
      when that origin is allowed.
    - Recommendation: accept exact allowed referer or `allowed + "/"`.

17. **Open redirect risk in admin-created URL shortener.**
    - Location: `server/app/routers/tools/urlshortener.py`.
    - `HttpUrl` blocks script schemes, but compromised admin access can create
      phishing redirects.
    - Recommendation: document accepted risk or add optional allow/block lists.

18. **No app-level health/readiness endpoint found.**
    - Compose checks db/redis, but the FastAPI app does not expose a clear
      readiness endpoint for app dependencies.
    - Recommendation: add `/api/health` or `/api/ready` with database/redis
      checks.

19. **Expired shared files are not proactively cleaned up.**
    - `get_by_code` rejects expired files, but disk and DB rows remain.
    - Recommendation: add scheduled cleanup and metrics/logging.

### P1 - PR #66 currency/expenses follow-ups

20. **Currency constants/defaults remain duplicated.**
    - Backend allowed currencies: `server/app/services/currency.py:12-16`.
    - Backend schemas: `server/app/schemas/tool_expense.py:7,32-35`.
    - Frontend constants: `client/src/composables/useExpenseFilters.ts:5-10`.
    - Seeds: `server/app/db/seed/builders.py`.
    - Recommendation: add parity tests or generate client constants from a
      single backend catalog.

21. **PLN-first client defaults conflict with backend USD defaults.**
    - Client default: `client/src/composables/useExpenseFilters.ts:7`.
    - Settings default: `server/app/settings.py:95`.
    - Backend create schema default: `server/app/schemas/tool_expense.py:35`.
    - Backend model server default: `server/app/db/models/tool_expense.py:15`.
    - Backend summary default: `server/app/routers/tools/expenses.py:125` and
      `server/app/services/tool_expense.py:205`.
    - Recommendation: decide whether PLN-first is a product invariant; if yes,
      align backend defaults too.

22. **Currency converter is embedded under expenses only.**
    - Frontend `/admin/tools/currency` redirects to the expenses converter tab:
      `client/src/router/index.ts:35-37`.
    - Backend has no `server/app/routers/tools/currency.py`; endpoints live at
      `/api/tools/expenses/rates` and `/api/tools/expenses/convert`.
    - Recommendation: either keep this as explicit product direction or restore
      separate currency routes and share the service.

23. **New converter has raw console error logging.**
    - Location: `client/src/components/expenses/ExpenseCurrencyConverter.vue:52-64`.
    - This matches existing client style, but many admin components repeat the
      same `console.error` plus toast pattern.
    - Recommendation: add a shared `runApiAction`/error helper later.

24. **New converter needs formatting cleanup.**
    - Prettier flags
      `client/src/components/expenses/ExpenseCurrencyConverter.vue`.

### P2 - DRY and maintainability backlog

25. **Frontend admin CRUD/error patterns are repeated.**
    - Repeated `console.error`, toast, and loading handling across tools.
    - Recommendation: introduce a small composable only when touching multiple
      admin pages.

26. **Repeated audit record construction.**
    - Domain services manually build similar `AuditRecord` values.
    - Recommendation: add helpers for common domain events.

27. **Pagination/filter boilerplate is repeated in routers.**
    - Tools routers repeat page/per-page/filter patterns.
    - Recommendation: centralize pagination helpers when expanding APIs.

28. **Platform/tool catalog is duplicated.**
    - Backend registry, frontend route slugs, dashboard links, and permission
      names can drift.
    - Recommendation: add a parity test or generated manifest.

29. **Expense categories are duplicated.**
    - Defaults appear in services, migrations, seed builders, client defaults,
      and tests.
    - Recommendation: centralize or add parity tests.

30. **Fat routers and mixed boundaries remain.**
    - Auth, vid-download, OAuth callbacks, expenses, and Telegram handlers mix
      I/O, validation, business logic, and presentation.
    - Recommendation: keep route handlers thin as future feature work touches
      them.

31. **Postgres-specific behavior is under-tested locally.**
    - Default pytest path uses SQLite with Postgres indexes stripped.
    - `pytest -m postgres` is optional and skipped without `POSTGRES_TEST_URL`.
    - Recommendation: add a CI job for Postgres-specific paths, especially FTS
      and constraints.

32. **Frontend coverage is still thin.**
    - Existing Vitest coverage is focused on composables and selected utilities.
    - Recommendation: add focused tests when changing admin tools, file-share,
      auth-cookie flows, and currency/expenses.

33. **Security workflow lacks container/image scanning.**
    - Current workflow covers gitleaks, pip-audit, npm audit, and CodeQL.
    - Recommendation: consider Trivy/Grype and SBOM generation for Docker images.

34. **Dependabot coverage can expand.**
    - Consider Docker and GitHub Actions ecosystems in addition to uv/npm.

35. **Floating infrastructure tags remain.**
    - Examples include broad Python/node/redis tags in Docker/Compose.
    - Recommendation: pin where reproducibility matters, balanced against this
      project's preference for current Alpine variants.

## Positive posture to preserve

- Locked Python and npm dependencies are committed.
- CodeQL succeeds on main.
- FastAPI auth uses bcrypt, JWT refresh rotation, Redis blacklist, and HttpOnly
  cookies in production.
- CSRF checks exist for cookie-authenticated mutating API requests in production.
- Redis-backed rate limiting uses an atomic Lua script.
- Video download uses `create_subprocess_exec`, not shell execution.
- No obvious `shell=True`, `eval`, unsafe YAML load, pickle usage, or committed
  live secrets were found in the targeted scans.
- Email preview uses DOMPurify before `v-html`.
- Sentry is configured with masked frontend replay and server PII disabled.
- Dockerfiles use non-root users and Alpine images.
- The repo already has good security documentation in `docs/security.md` and
  `SECURITY.md`.

## Suggested future task order

1. Fix `.github/workflows/security.yml` so pip-audit runs on CI.
2. Upgrade or override `aiohttp` to 3.14.0+ and validate Telegram bot flows.
3. Run focused Ruff and Prettier cleanup.
4. Fix file-share prod nginx route, upload limit, and public media bypass.
5. Redact console email body previews.
6. Harden trusted client IP handling for rate limits.
7. Enforce Telegram allowlist when bot tokens are configured in production.
8. Align PLN-first expense/currency defaults or document why backend defaults
   remain USD.
9. Restore request-log user correlation.
10. Add health/readiness endpoints and cleanup for expired shared files.
