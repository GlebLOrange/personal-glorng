# Project Review — gLOrng Portfolio & Platform

## 2026-08-09 — Architecture & System State Review

### 1. Executive Summary
**gLOrng** is a full-stack developer portfolio and personal platform built with FastAPI, Vue 3, MongoDB (via Motor), and Redis. It is containerized using Docker Compose with multiple operation modes (Lite default, Ultra-Lite, Docker client, Production).

---

### 2. Stack & Components Overview

* **Backend (`server/`)**:
  * **Framework**: FastAPI with Python 3.12+ (managed by `uv`).
  * **Database & Storage**: MongoDB (primary document store via Motor), Redis (cache & session storage), optional PostgreSQL for secondary audit/FTS storage.
  * **Background Tasks & Services**: Celery + RabbitMQ (broker) for async processing; Telegram todobot (`server/app/todobot`); search re-indexing workers.
  * **Code Quality & Testing**: `ruff` for linting/formatting, `pytest` for unit/integration testing.

* **Frontend (`client/`)**:
  * **Framework**: Vue 3 (Composition API), Vite, TypeScript (pinned `~5.8.3`).
  * **State & Styling**: Pinia, Tailwind CSS, Monospace & Toss-style UI design aesthetics.
  * **Testing & Tooling**: Vitest, Playwright E2E, ESLint.

* **Infrastructure & Orchestration**:
  * **Reverse Proxy**: Nginx (:80) routing to API (:8000) and frontend.
  * **Vite Dev**: Host server (:3000) in lite mode.

---

### 3. Execution & Development Modes

| Mode | Command | Active Services |
|---|---|---|
| **Lite (Default)** | `make dev` + `make dev-lite-client` | MongoDB, Redis, API, Nginx in Docker + Host Vite |
| **Ultra-Lite** | `make dev-ultra-lite-infra` | MongoDB, Redis in Docker + Host API (`make dev-ultra-lite-server`) |
| **Full Docker** | `make dev-docker` | All services including Vite client container in Docker |
| **Search-enabled** | `make dev-search` | Adds Elasticsearch container profile |

---

### 4. Key Project Conventions & Guardrails

* **Environment Contracts**: Defined in `.env.example`. Secrets like `JWT_SECRET` (32+ chars), `SEED_PASSWORD` (12+ chars satisfying complexity rules), `REDIS_PASSWORD`, and `MONGODB_PASSWORD` must be set.
* **Testing Standard**: Backend unit tests run via isolated venv (`UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv`). Frontend tests run via `npm run test:coverage`.
* **Documentation**: Published VitePress handbook under `docs/` (`make docs-dev` / `make docs-generate`).

---

### 5. Truth Map & Key Files

* **Agents & Bootstrap**: [`AGENTS.md`](file:///Users/glorange/projects/portfolio-glorng/AGENTS.md)
* **Project Rules**: [`.cursor/rules/`](file:///Users/glorange/projects/portfolio-glorng/.cursor/rules)
* **Project Skills**: [`.cursor/skills/`](file:///Users/glorange/projects/portfolio-glorng/.cursor/skills)
* **Handbook & Architecture Docs**: [`docs/index.md`](file:///Users/glorange/projects/portfolio-glorng/docs/index.md) & [`docs/adr/`](file:///Users/glorange/projects/portfolio-glorng/docs/adr)
