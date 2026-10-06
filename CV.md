# Gleb Yuryev
**Python Backend Engineer | FastAPI | REST APIs | Async Systems**

Wrocław, Poland · Open to remote / full-time / contract  
glorange@gmail.com · GitHub: github.com/GlebLOrange · LinkedIn: linkedin.com/in/glorange

## PROFILE

Python backend engineer building REST APIs, authentication, background workers, automation, and containerized deploys. Strong focus on FastAPI, asynchronous Python, Redis/Celery, databases, API security, testing, and Docker/Linux ops.

Owns the path from data modeling and API design through tests, CI/CD, and deployment. Owns the Vue client when the product needs one.

Live sample: this portfolio platform (auth, workers, search, OpenAPI, tests, CI).

## TECHNICAL SKILLS

**Languages:** Python, SQL, TypeScript, JavaScript

**Backend:** FastAPI, REST APIs, Pydantic, SQLAlchemy, async Python, authentication, RBAC, background processing

**Databases & Search:** PostgreSQL, MongoDB, Redis, Elasticsearch

**Async & Messaging:** Celery, RabbitMQ, Redis

**Testing & Quality:** pytest, pytest-asyncio, coverage (fail-under 65), Ruff, mypy

**DevOps:** Docker, Docker Compose, Nginx, Linux, GitHub Actions, CI/CD

**Integrations & Automation:** Telegram bots, Google APIs, third-party APIs, scheduled jobs, CLI tools

**Frontend:** Vue 3, TypeScript, Pinia, Tailwind CSS

**Observability:** Sentry, OpenTelemetry (opt-in)

## EXPERIENCE

### Independent Python Backend Engineer
**Independent — personal developer platform | 2022–Present**

Operate a public FastAPI + Vue hiring sample: cookie auth, CSRF, SSRF-safe fetches, workers, search, and CI.

- Designed REST APIs with FastAPI, Pydantic validation, capability RBAC, fail-closed rate limiting, and OpenAPI docs.
- Cookie auth with HttpOnly sessions, CSRF origin checks on mutating `/api` (staging/production), Bearer clients unaffected.
- Outbound fetches cannot reach private networks; covered by unit tests (SSRF-safe public DNS path).
- Celery/Redis workers for email, task automation, news ingest, and cleanup without blocking API requests.
- Multi-service Docker Compose + Nginx; GitHub Actions CI (Ruff, mypy, pytest, security checks, e2e); Sentry and opt-in OpenTelemetry.

### Freelance Backend & Full-Stack Engineer
**Independent / client projects | 2017–2022**

API, admin, and automation work for small teams — typically solo delivery from schema through deploy.

- Built REST APIs with authentication, caching, and third-party integrations (payments, messaging) that small teams could operate without a dedicated backend hire.
- Admin dashboards and internal automation: Telegram bots, scheduled jobs, CLI maintenance tools.
- Docker + Nginx reverse-proxy deploys with environment-based configuration.

## CASE STUDIES

### Cookie auth & CSRF
**FastAPI · cookies · CSRF · RBAC · Redis**

Problem: Cookie auth on a Vue SPA is open to CSRF unless mutating API calls check Origin; Bearer API clients must keep working.

Approach: HttpOnly cookie sessions with capability RBAC; CSRF origin checks on mutating `/api` in staging/production; Bearer-only requests skip CSRF; auth rate limits fail closed when Redis is down.

Result: Documented security path with CSRF middleware tests; bad Origin rejected in production; Bearer automation unaffected.

Docs: https://gleblorange.github.io/personal-glorng/reference/security.html#csrf-and-cors

### SSRF-safe outbound fetch
**Python · httpx · asyncio · DNS**

Problem: Server-side HTTP for news and health checks must not reach private networks; connecting to a resolved IP without SNI breaks TLS; redirect joins against the IP URL drop the original host.

Approach: Resolve public DNS off the event loop, connect to that IP with Host + SNI hostname, re-validate every redirect hop, join `Location` against the pre-rewrite URL.

Result: Fail-closed public fetch with unit coverage for SNI, relative redirects, and off-loop DNS — used by outbound tool paths.

Code: https://github.com/GlebLOrange/personal-glorng/blob/main/server/app/core/url_safety.py

## EDUCATION

### [Degree, course, or focus]
**[School or provider] | [Years]**

- Relevant to Python / FastAPI work: [APIs, databases, async, or systems you can discuss].

<!-- Drop this section from a sent PDF until the brackets above are real facts. -->

## ADDITIONAL

Open to **Python Backend / FastAPI** roles where API development, databases, asynchronous processing, testing, and Docker/Linux experience are the core of the job.
