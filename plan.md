# Portfolio plan

Living roadmap. Update **one section** when status changes.

| Section | Status |
|---------|--------|
| Expenses calculator | done |
| Currency converter | done |
| AI Chat off | done |
| Admin task create | done |
| sitemap.xml | done |

## Expenses calculator

**Status:** done

**Goal:** Personal monthly expense ledger — log spending for a month, see total and breakdown with graphs.

**Scope:**
- Calendar month picker (this month / last month / custom)
- Description + category as primary fields (DB column `tool_name` stores description)
- Hero month total; category-first charts
- Optional `?month=YYYY-MM` on list and summary APIs

**Key files:** `client/src/pages/admin/tools/ExpensesTool.vue`, `server/app/services/tool_expense.py`, `server/app/routers/tools/expenses.py`, `server/app/platform/registry.py`

**Acceptance:** Select a month, add mixed-currency items, see converted total and category charts.

**Notes:** Shipped on `cursor/portfolio-roadmap` — month picker, category-first charts, description labels.

---

## Currency converter

**Status:** done

**Goal:** Standalone admin tool to convert amounts between EUR, USD, PLN, and BYN.

**Scope:**
- `GET /api/tools/currency/rates`, `POST /api/tools/currency/convert`
- `CurrencyConverterTool.vue` admin page
- Platform registry + router entry

**Key files:** `server/app/routers/tools/currency.py`, `server/app/schemas/currency.py`, `client/src/pages/admin/tools/CurrencyConverterTool.vue`

**Acceptance:** 100 EUR → PLN matches server-side conversion using cached rates.

**Notes:** Shipped — `/api/tools/currency/*` and admin UI at `/admin/tools/currency`.

---

## AI Chat

**Status:** done

**Goal:** Disable AI chat without removing code; re-enable via env flag.

**Scope:**
- `AI_CHAT_ENABLED` / `VITE_AI_CHAT_ENABLED` settings
- API returns 503 when disabled
- Hidden from platform catalog and dashboard

**Key files:** `server/app/settings.py`, `server/app/routers/tools/ai_chat.py`, `server/app/routers/platform.py`, `client/src/router/index.ts`

**Acceptance:** No dashboard tile; API 503; flag `true` restores behavior.

**Notes:** Shipped — default off via `AI_CHAT_ENABLED` / `VITE_AI_CHAT_ENABLED`.

---

## Admin tasks

**Status:** done

**Goal:** Create tasks from the admin panel (same model as Telegram bot).

**Scope:**
- `POST /api/tools/tasks` with `TaskCreate` schema
- Defaults `telegram_user_id` to `TELEGRAM_ALLOWED_USER_ID`
- Enqueue Google Calendar sync on create
- Form on `TasksPage.vue`

**Key files:** `server/app/routers/tools/tasks_admin.py`, `server/app/schemas/task.py`, `client/src/pages/admin/tools/TasksPage.vue`

**Acceptance:** Admin creates task; it appears in list for the configured Telegram user.

**Notes:** Shipped — `POST /api/tools/tasks` + create form on Tasks page.

---

## sitemap.xml

**Status:** done

**Goal:** Valid `sitemap.xml` and `robots.txt` for public SEO.

**Scope:**
- Public routes: `/`, `/privacy` (exclude admin, `/callback`, `/login`)
- FastAPI serves XML using `BASE_URL`
- Nginx proxies `/sitemap.xml` and `/robots.txt` to API in prod

**Key files:** `server/app/routers/seo.py`, `server/app/main.py`, `nginx/nginx.conf`, `nginx/nginx.prod.conf`

**Acceptance:** `curl /sitemap.xml` returns valid XML with absolute URLs.

**Notes:** Shipped — `GET /sitemap.xml` and `GET /robots.txt` via API; nginx proxies in dev/prod.

---

## Deferred infrastructure

**Status:** backlog

**Goal:** Heavy or hosting-dependent optimizations deferred until they justify the cost.

**Later (not in dev compose today):**
- Elasticsearch/OpenSearch for unified admin search (~512MB+ steady RAM)
- CDN / edge cache (Cloudflare, HTTP/3, brotli at edge)
- Optional slim dev API image without `ffmpeg`/`yt-dlp` for frontend-only work
- Lighthouse CI, self-hosted fonts (public site perf, not dev RAM)
- Public portfolio search (resume is static JSON until content is DB-backed)

**Shipped locally instead:**
- Compose profiles: worker and todobot off by default (`make dev`)
- `make dev-lite`: db + redis + API only; Vite on host
- Dev memory caps on Postgres/Redis; Sentry profiling disabled in development
- Postgres full-text search for recipes (title, ingredients, steps, notes)
