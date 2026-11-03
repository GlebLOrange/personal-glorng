# AGENTS.md

Dispatch only. Do not put bootstrap recipes, ports, or skill bodies here.

Shared entry for Cursor, Antigravity, Claude, and Gemini. Skills and rules stay under [`.cursor/`](.cursor/); Antigravity and Claude reach them through [`.agents/`](.agents/) and [`.claude/`](.claude/) (symlinks and activation files).

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

Gemini: tooling (Gortex MCP + hooks) lives in [`.gemini/settings.json`](.gemini/settings.json); `GEMINI.md` and `CLAUDE.md` only point here — edit this file, not them.

<!-- gortex:communities:start -->
## Community Skills

| Area | Description | Explore |
|------|-------------|---------|
| App Services 13 Dirs Record | 438 symbols | `analyze(operation:"communities", id:"community-400")` |
| Tests 6 Dirs Get | 412 symbols | `analyze(operation:"communities", id:"community-536")` |
| Components Ui 30 Dirs | 361 symbols | `analyze(operation:"communities", id:"community-54")` |
| Composables 4 Dirs Usetasks | 358 symbols | `analyze(operation:"communities", id:"community-123")` |
| Tests 3 Dirs Post | 354 symbols | `analyze(operation:"communities", id:"community-533")` |
| Tests 13 Dirs | 301 symbols | `analyze(operation:"communities", id:"community-546")` |
| App Services 20 Dirs | 289 symbols | `analyze(operation:"communities", id:"community-485")` |
| Db Repositories 7 Dirs | 264 symbols | `analyze(operation:"communities", id:"community-420")` |
| Tests 15 Dirs | 258 symbols | `analyze(operation:"communities", id:"community-507")` |
| App Schemas 10 Dirs | 252 symbols | `analyze(operation:"communities", id:"community-429")` |
| Tests 10 Dirs | 241 symbols | `analyze(operation:"communities", id:"community-530")` |
| Tests 9 Dirs | 203 symbols | `analyze(operation:"communities", id:"community-547")` |
| App Services 7 Dirs | 184 symbols | `analyze(operation:"communities", id:"community-488")` |
| Composables 10 Dirs | 176 symbols | `analyze(operation:"communities", id:"community-74")` |
| App Services 13 Dirs Apierror | 161 symbols | `analyze(operation:"communities", id:"community-472")` |
| Db Documents 8 Dirs | 160 symbols | `analyze(operation:"communities", id:"community-466")` |
| 9 Dirs | 155 symbols | `analyze(operation:"communities", id:"community-459")` |
| App Core 12 Dirs | 150 symbols | `analyze(operation:"communities", id:"community-401")` |
| Tests 6 Dirs Create User | 138 symbols | `analyze(operation:"communities", id:"community-518")` |
| Tests 11 Dirs | 136 symbols | `analyze(operation:"communities", id:"community-477")` |

<!-- gortex:communities:end -->
