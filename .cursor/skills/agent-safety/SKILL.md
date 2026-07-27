---
name: agent-safety
description: Guardrails for commits, destructive actions, sensitive files, and when to run tests
---

# Agent safety

- Never commit unless the user explicitly requests it.
- Never push to `main` unless the user explicitly requests it.
- Never run destructive or irreversible git commands (force push, hard reset) unless explicitly requested.
- Never delete config, migrations, index scripts, or env files without explicit user confirmation.
- Never commit `.env`, credentials, or other secret-bearing files.

## Tests

- Do **not** run unit/integration/E2E tests by default during implementation.
- When implementation for the current ask is done (or before claiming “tests pass”), ask once: **“Run tests for this change?”**
- Run tests only if the user says yes, already asked to run/pass/verify tests, or the task is explicitly test-focused (writing/fixing tests, CI failure).
- Prefer targeted files when they opt in; full suite only if they ask for it.
- Never claim tests passed if none were run.
