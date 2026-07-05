# Contributing

How to change gLOrng and open a pull request.

## Branch workflow

1. Branch from `main`: `cursor/<short-kebab-description>` (agents) or your own feature branch name.
2. Make focused changes; avoid unrelated files.
3. Run targeted checks before pushing (see below).
4. Open a PR with a short title and **Summary** + **Test plan** sections.

Do not push directly to `main`. Never commit `.env` or credentials.

## Backend checks

```bash
cd server
uv sync --frozen
uv run ruff check .
uv run pytest -m "not integration" -v
```

In Docker (when stack is up): `make lint-check` and `make test`.

## Frontend checks

```bash
cd client
npm ci
npm run lint
npm run test
npm run build:check
```

## Full gate (CI-equivalent)

```bash
make check
cd client && npm run e2e   # optional; needs running API
```

CI workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). Testing tiers: [Testing](/reference/testing).

## Pre-commit

```bash
pip install pre-commit && pre-commit install
```

Runs ruff, client eslint/prettier/typecheck, and gitleaks.

## Code conventions

- **Python:** Ruff, type annotations on functions, pytest for tests under `server/tests/`
- **Vue/TS:** ESLint + Prettier; match existing component and composable patterns
- **Dependencies:** check `server/pyproject.toml` and `client/package.json` before adding packages
- **Agents:** see [AGENTS.md](../../AGENTS.md) and [`.cursor/rules/`](../../.cursor/rules/)

## Documentation

When changing behavior, update the relevant page under `docs/` and run:

```bash
make docs-build
```

## Security

See [SECURITY.md](../../SECURITY.md) for vulnerability disclosure. Security posture: [Security](/reference/security).
