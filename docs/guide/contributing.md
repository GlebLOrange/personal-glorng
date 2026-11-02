# Contributing

How to change Gleb.Y and open a pull request.

## Branch workflow

1. Branch from `main`: `cursor/<short-kebab-description>` (agents) or your own feature branch name.
2. Make focused changes; avoid unrelated files.
3. Run targeted checks before pushing (see [Quality checks](/guide/development#quality-checks) and [Testing](/reference/testing)).
4. Open a PR with a short title and **Summary** + **Test plan** sections.

Do not commit or push to `main` unless asked. Never commit `.env` or credentials.

- **2026-10-30:** Prefer only `main` + the current checkout locally. When cleaning, remove unused worktrees first, then delete other local `cursor/*` (merged, gone-upstream, or abandoned locals even if `origin/cursor/…` still exists). Leave remotes unless asked. Never delete a branch checked out in a live worktree. `git fetch --prune` / `git worktree prune` as supporting steps.
- **2026-10-26:** Local cleanup deletes only branches merged into `main` and branches whose upstream is gone. Keep `main` and any branch checked out in a live worktree; `git fetch --prune` drops stale remote-tracking refs. Leave unmerged branches that still have a remote. Superseded 2026-10-30.

## Where facts live

| Topic | Page |
|-------|------|
| First-run setup and secrets | [Getting started](/guide/getting-started) |
| Dev modes, ports, quality commands | [Development](/guide/development) |
| Channels, stores, request pipeline | [Architecture](/guide/architecture) |
| Service catalog and terminology | [Platform overview](/reference/platform) |
| Test tiers and markers | [Testing](/reference/testing) |
| Handbook information architecture | [Handbook structure](/specs/handbook-structure) |

## Checks

Backend, frontend, and local full-gate commands: [Development → Quality checks](/guide/development#quality-checks).

`make check` is a local convenience gate — CI also runs coverage, `not integration`, postgres, e2e, and docs freshness. Workflow: [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml). Testing tiers: [Testing](/reference/testing).

Merge gates (`ci-ok`, `gitleaks`) are **disabled during development**; turn them on before production — [DevOps checklist](/operations/devops-checklist#development-vs-production-github--cicd).

## Pre-commit

```bash
pip install pre-commit && pre-commit install
```

Runs ruff, client eslint/prettier/typecheck, gitleaks, and a **staged file token limit** (rejects staged text files over 5,000 tokens; `1 token = 4 bytes`). Skip patterns live in [`scripts/staged-token-limit.ignore`](../../scripts/staged-token-limit.ignore) (lockfiles, minified/generated paths, common binaries). Manual pass/fail check:

```bash
sh scripts/test_check_staged_token_limit.sh
```

## Code conventions

- **Python:** Ruff, type annotations on functions, pytest for tests under `server/tests/`
- **Vue/TS:** ESLint + Prettier; match existing component and composable patterns
- **Dependencies:** check `server/pyproject.toml` and `client/package.json` before adding packages
- **Agents:** [AGENTS.md](../../AGENTS.md) (entry map), [CODING_STANDARDS.md](../../CODING_STANDARDS.md) (skill index), [`.cursor/agents/README.md`](../../.cursor/agents/README.md). Keep skill and rule bodies in [`.cursor/skills/`](../../.cursor/skills/) and [`.cursor/rules/`](../../.cursor/rules/). Tracked [`.agents/`](../../.agents/) and [`.claude/`](../../.claude/) symlinks activate the same config for Antigravity and Claude; do not commit `skills-lock.json` or other local skill mirrors.

## Documentation

When changing behavior, update the relevant page under `docs/` (see the ownership table above) and run:

```bash
make docs-build
```

## Security

See [SECURITY.md](../../SECURITY.md) for vulnerability disclosure. Security posture: [Security](/reference/security).
