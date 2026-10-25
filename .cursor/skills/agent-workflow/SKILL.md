---
name: agent-workflow
description: Branch before edits, safety for commits/secrets/destructive git and tests, and verify packages before new imports
---

# Agent workflow

## Git branch

Before editing tracked project files:

1. Check the current branch (`git branch --show-current`).
2. If on `main` (or another shared branch), **ask the user once** whether to create `cursor/<short-kebab-description>` and create it before edits.
3. Use branch prefix **`cursor/`** only (example: `cursor/fix-nginx-csp`).
4. Do not commit or push to `main` unless the user explicitly requests it.

For new chats or risky/experimental work, prefer Cursor **Worktree** mode or start with `/worktree <task>` so changes stay isolated.

When the user asks to commit or open a PR, inspect status, diff, and recent history first; never commit, push, amend, or open a PR unless explicitly requested.

## Safety

- Never commit unless the user explicitly requests it.
- Never push to `main` unless the user explicitly requests it.
- Never run destructive or irreversible git commands (force push, hard reset) unless explicitly requested.
- Never delete config, migrations, index scripts, or env files without explicit user confirmation.
- Never commit `.env`, credentials, or other secret-bearing files.

## Dependencies

Before adding an import or dependency:

1. Check `server/pyproject.toml` or `client/package.json` for an existing entry.
2. Verify with `uv pip show <pkg>` (Python) or `npm list <pkg>` (Node) when unsure.

Do not invent package names, modules, or APIs.

## Tests

- Do **not** run unit/integration/E2E tests by default during implementation.
- When implementation for the current ask is done (or before claiming “tests pass”), ask once: **“Run tests for this change?”**
- Run tests only if the user says yes, already asked to run/pass/verify tests, or the task is explicitly test-focused (writing/fixing tests, CI failure).
- Prefer targeted files when they opt in; full suite only if they ask for it.
- Never claim tests passed if none were run.
