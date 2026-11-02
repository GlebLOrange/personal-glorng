# Gemini

Coding instructions for this repo when running under Gemini CLI / Gemini Code Assist.

## Always load first

1. [`AGENTS.md`](AGENTS.md) — dispatch map (what to read before which kind of edit)
2. [`CODING_STANDARDS.md`](CODING_STANDARDS.md) — skill index (open the matching skill; do not paste skill bodies here)
3. Always-on rules (read the file, then follow it):
   - [`.cursor/rules/project-context.mdc`](.cursor/rules/project-context.mdc) — product goal, real stack, change guardrails
   - [`.cursor/rules/agent-workflow.mdc`](.cursor/rules/agent-workflow.mdc) → skill [`.cursor/skills/agent-workflow/SKILL.md`](.cursor/skills/agent-workflow/SKILL.md) — branch before edits, no unrequested commit/push/secrets, ask before tests
   - [`.cursor/rules/gortex-workflow.mdc`](.cursor/rules/gortex-workflow.mdc) — prefer Gortex graph tools over whole-file reads when available

Path-triggered rules (same content as Antigravity under [`.agents/rules/`](.agents/rules/)):

| Paths | Rule |
|-------|------|
| `server/**/*.py` | [`.cursor/rules/python-fast-api.mdc`](.cursor/rules/python-fast-api.mdc) |
| `client/src/**/*.{ts,vue}` | [`.cursor/rules/vue.mdc`](.cursor/rules/vue.mdc) |
| Client ↔ API | [`.cursor/rules/client-server.mdc`](.cursor/rules/client-server.mdc) |
| Vue layout / CSS / a11y | [`.cursor/rules/client-ui.mdc`](.cursor/rules/client-ui.mdc) |

## Product (short)

Personal portfolio/CV site (Gleb.Y). Goal: clear technical experience for IT / Python / backend interviews. Stack to verify in-repo: FastAPI + Motor/Mongo (+ optional Postgres/Redis/Celery), Vue 3 + Vite + TypeScript + Tailwind + Pinia, Nginx + Docker Compose. Do not assume React/Nuxt/Svelte.

## How to work here

- Inspect architecture first; smallest fix; no new deps or large architecture shifts without approval.
- Before editing tracked files: if on `main`, ask once to create `cursor/<short-kebab>` and switch before edits. Never commit, push, or force-push unless explicitly asked. Never commit `.env` or secrets.
- Before a new import: check `server/pyproject.toml` / `client/package.json` (and `uv pip show` / `npm list` if unsure).
- Do not run unit/integration/E2E suites by default; ask once “Run tests for this change?” when implementation is done, unless the user already asked for tests.
- Skills and personas live under [`.cursor/`](.cursor/). Prefer those over inventing process.

## Gemini tooling in this repo

Configured in [`.gemini/settings.json`](.gemini/settings.json):

- MCP: `gortex` (`gortex mcp`)
- Hooks: `SessionStart` and `AfterTool` run `gortex hook --agent gemini` (graph context + stale-index hint)

When Gortex MCP is available: start with `explore` (`operation: "task"`), prefer `search` / `read` / `relations` / `trace` over repo-wide greps, call `change` impact before mutation, mutate with `edit`/`refactor`, then `detect` / `tests` / `guards` / `contract`. If Gortex is missing or `repo_not_tracked`: say so once, then use normal read/search/edit. Do not invent graph results. Do not run `gortex track` unless asked.

Gortex code areas: `analyze(operation:"communities")` or [`.cursor/references/gortex-communities.md`](.cursor/references/gortex-communities.md).

## Setup / ops pointers

- Env and ports: [`docs/guide/getting-started.md`](docs/guide/getting-started.md), [`README.md`](README.md)
- Contributing / checks: [`docs/guide/contributing.md`](docs/guide/contributing.md)
- Ops commands: [`.cursor/commands/ops.md`](.cursor/commands/ops.md), [`.cursor/commands/maintain.md`](.cursor/commands/maintain.md)
- Cloud VM Docker: [`docs/operations/cloud-vm.md`](docs/operations/cloud-vm.md)
- Personas: [`.cursor/agents/README.md`](.cursor/agents/README.md)
