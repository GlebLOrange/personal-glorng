# Project contract (harness)

**Product:** Gleb.Y — personal portfolio/CV aimed at Python/backend/IT hiring signal.

**Canonical Cursor policy:** `.cursor/rules/project-context.mdc`, `AGENTS.md`

## Stack (verify in repo before acting)

- Backend: FastAPI, Motor (MongoDB), optional Postgres, Redis, Celery/RabbitMQ (opt-in)
- Frontend: Vue 3, Vite, TypeScript, Tailwind, Pinia
- Ops: Nginx, Docker Compose
- Quality: uv, Ruff, pytest; ESLint, Vitest, Playwright

## Change guardrails

1. Inspect architecture before editing.
2. Preserve existing behavior; minimal diff.
3. No new dependencies without explicit approval.
4. No large architecture changes without human approval.
5. Run targeted tests before claiming done.

## Two AI systems (do not conflate)

| System | Location | Purpose |
|--------|----------|---------|
| Site AI | `server/app/services/ai_chat.py`, `task_intake` | End-user features, feature-flagged |
| Dev harness | `ai/`, `.cursor/`, DSH | Building the site |
