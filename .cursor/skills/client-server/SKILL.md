---
name: client-server
description: How the Vue client and FastAPI server meet — request path, useApi, and page-to-router-to-service pairing.
---
# Client / server contract

Use this when changing code under `client/src` or `server/` so the two sides stay on the same path.

## Request path

Browser hits nginx.

- `/` and `/admin` go to the Vue app.
- `/api` goes to FastAPI.

Lite default (`make` / `make dev`): MongoDB, Redis, API, and nginx in Docker; Vite on the host. Postgres, Celery/RabbitMQ, Elasticsearch, and the client container stay opt-in.

Human handbook: `docs/guide/architecture.md`.

## Client calls

- HTTP goes through `client/src/composables/useApi.ts` (and helpers such as `useApiAction`). Do not add another HTTP client.
- Pinia owns the auth session only (`client/src/stores/auth.ts`). Keep other server state in composables or the page.
- A feature page lives under `client/src/pages` (public, `pages/tools`, or `pages/admin`).

## Server path

- Thin router under `server/app/routers` (or `routers/tools`, `routers/admin`): auth, validation, status mapping, dependencies.
- Business logic under `server/app/services`.
- MongoDB is primary. Redis covers cache, rate limits, and sessions. Postgres, Celery/RabbitMQ, and Elasticsearch stay opt-in.

## Feature pairing

Page or composable → `useApi` → `/api/...` → thin router → service → MongoDB / Redis.

The Vue page is another channel into the same service layer (same pattern as the Telegram bot and Celery workers).

## Do not

- Call the database from Vue.
- Put business logic in the router.
- Invent a second fetch stack beside `useApi`.
