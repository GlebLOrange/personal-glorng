# Backend harness notes

**Entry:** `server/` — FastAPI, async Mongo via Motor.

**Standards:** `.cursor/skills/python-fast-api/SKILL.md`, `.cursor/rules/python-fast-api.mdc`

**Checks (host, CI-aligned):**

```bash
cd server
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv sync --frozen
UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run ruff check .
GLORNG_ENV_FILE=$PWD/tests/.env.test \
  UV_PROJECT_ENVIRONMENT=/tmp/glorng-server-venv uv run pytest -v
```

Run targeted pytest paths for small changes; full suite before merge is human/CI choice.
