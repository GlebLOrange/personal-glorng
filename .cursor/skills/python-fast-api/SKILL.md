---
name: python-fast-api
description: FastAPI and Python backend guidance for the server package.
---
# FastAPI Backend

Use this when changing Python code under `server/`.

## Project Fit

- Source lives under `server/app`; tests live under `server/tests`.
- Dependencies are managed by `uv` in `server/pyproject.toml` and `server/uv.lock`.
- Ruff is the source of truth for formatting and linting.
- Configuration belongs in environment-backed settings, not hardcoded constants.
- Primary data store is Motor/MongoDB. Optional Postgres is secondary. Do not assume SQLAlchemy, Alembic, Poetry, or `fastapi-users`.

## Key Principles

- Keep route handlers thin: authentication, validation, HTTP status mapping, and dependency wiring belong in routers; business logic belongs in services.
- Prefer small functions and existing services over new abstractions.
- Use descriptive `snake_case` names with clear state booleans such as `is_active` and `has_permission`.
- Use Pydantic models for request/response validation instead of raw dictionaries at API boundaries.
- Validate external input at the boundary and keep authorization checks close to protected routes or service entrypoints.

## Python Style

- Add type annotations to new or changed function signatures, including explicit `-> None` where applicable.
- Add docstrings when they explain non-obvious behavior, public APIs, fixtures, or test intent. Do not add boilerplate docstrings that only repeat the function name.
- Keep existing comments unless they are stale because of the current change.
- Prefer standard library and existing helpers before adding dependencies.

## FastAPI

- Use `async def` for I/O-bound routes and services.
- Use `def` for pure CPU-local helpers.
- Prefer FastAPI dependencies for shared request state and permission checks.
- Raise `HTTPException` for expected HTTP errors; log unexpected failures without leaking secrets or stack traces to users.
- Prefer lifespan setup over new `@app.on_event` handlers.

## Error Handling

- Handle invalid state with guard clauses before the happy path.
- Avoid broad exception handling unless the code adds useful context or maps to a safe user-facing error.
- Never log passwords, tokens, API keys, full cookies, or sensitive request bodies.

## Data And Performance

- Use async database clients and avoid blocking I/O in request handlers.
- Keep list endpoints paginated or explicitly bounded.
- Check MongoDB/PostgreSQL indexes before adding query patterns that sort, filter, or search at scale.
- Treat Redis, RabbitMQ, external APIs, and LLM output as fallible external boundaries.

## Tests

- Use pytest only; do not introduce `unittest`.
- Put backend tests under `server/tests`.
- Keep tests behavior-focused and as small as possible.
- Import pytest typing helpers under `TYPE_CHECKING` only when a test actually needs them.

## Verification

- For backend changes, prefer targeted `uv run ruff check <path>` and focused pytest files.
- Run broader backend checks only when the change crosses shared contracts, CI is failing, or the user asks.
