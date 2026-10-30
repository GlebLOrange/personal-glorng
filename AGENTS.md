# AGENTS.md

Dispatch only. Do not put bootstrap recipes, ports, or skill bodies here.

Shared entry for Cursor, Antigravity, and Claude. Skills and rules stay under [`.cursor/`](.cursor/); Antigravity and Claude reach them through [`.agents/`](.agents/) and [`.claude/`](.claude/) (symlinks and activation files).

| Before you… | Read |
|-------------|------|
| Edit application code | [`CODING_STANDARDS.md`](CODING_STANDARDS.md) |
| Change FastAPI routes, schemas, or OpenAPI docs | [`docs/guide/contributing.md`](docs/guide/contributing.md), [`scripts/generate_docs.py`](scripts/generate_docs.py); regenerate documented API artifacts rather than editing generated outputs |
| Change a client–server API path or contract | [`.cursor/skills/client-server/SKILL.md`](.cursor/skills/client-server/SKILL.md), [`.cursor/skills/python-fast-api/SKILL.md`](.cursor/skills/python-fast-api/SKILL.md) |
| Edit FastAPI routes, services, or schemas | [`.cursor/skills/python-fast-api/SKILL.md`](.cursor/skills/python-fast-api/SKILL.md) |
| Change Vue UI layout, styling, motion, forms, or accessibility | [`.cursor/skills/client-ui/SKILL.md`](.cursor/skills/client-ui/SKILL.md), [`.cursor/skills/vue/SKILL.md`](.cursor/skills/vue/SKILL.md) |
| Set up env, run services, or run checks | [`docs/guide/getting-started.md`](docs/guide/getting-started.md), [`docs/guide/contributing.md`](docs/guide/contributing.md), [`README.md`](README.md); avoid routine test suites during development unless requested or risk/milestone warrants them |
| Start a stack, back up, or maintain the DB | [`.cursor/commands/ops.md`](.cursor/commands/ops.md) (`/ops`); preflight [`.cursor/commands/maintain.md`](.cursor/commands/maintain.md) (`/maintain`) |
| Use Docker on a Cursor Cloud VM | [`docs/operations/cloud-vm.md`](docs/operations/cloud-vm.md) |

Personas: [`.cursor/agents/README.md`](.cursor/agents/README.md). Orchestration: [`.cursor/commands/task-loop.md`](.cursor/commands/task-loop.md).

Gortex code areas: `analyze(operation:"communities")` or [`.cursor/references/gortex-communities.md`](.cursor/references/gortex-communities.md).
