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

<!-- gortex:communities:start -->
## Community Skills

| Area | Description | Explore |
|------|-------------|---------|
| Tests 17 Dirs | 665 symbols | `analyze(operation:"communities", id:"community-400")` |
| Tests 5 Dirs | 388 symbols | `analyze(operation:"communities", id:"community-512")` |
| Composables 4 Dirs Usetasks | 352 symbols | `analyze(operation:"communities", id:"community-119")` |
| Tests 3 Dirs | 345 symbols | `analyze(operation:"communities", id:"community-509")` |
| App Services 11 Dirs Delete | 339 symbols | `analyze(operation:"communities", id:"community-444")` |
| Components Ui 29 Dirs | 336 symbols | `analyze(operation:"communities", id:"community-56")` |
| Tests 10 Dirs | 255 symbols | `analyze(operation:"communities", id:"community-506")` |
| App Schemas 8 Dirs | 247 symbols | `analyze(operation:"communities", id:"community-409")` |
| App Services 15 Dirs | 208 symbols | `analyze(operation:"communities", id:"community-460")` |
| Tests 7 Dirs | 186 symbols | `analyze(operation:"communities", id:"community-515")` |
| 8 Dirs App Core Logging Logger | 185 symbols | `analyze(operation:"communities", id:"community-438")` |
| App Services 8 Dirs Record | 163 symbols | `analyze(operation:"communities", id:"community-436")` |
| Composables 7 Dirs Replace | 157 symbols | `analyze(operation:"communities", id:"community-213")` |
| App Services 7 Dirs Upsert | 157 symbols | `analyze(operation:"communities", id:"community-463")` |
| Tests 9 Dirs | 153 symbols | `analyze(operation:"communities", id:"community-399")` |
| Tests 6 Dirs Create User | 150 symbols | `analyze(operation:"communities", id:"community-496")` |
| App Services 10 Dirs Validationerror | 135 symbols | `analyze(operation:"communities", id:"community-378")` |
| Composables 8 Dirs | 124 symbols | `analyze(operation:"communities", id:"community-76")` |
| App Services 10 Dirs Create Article | 116 symbols | `analyze(operation:"communities", id:"community-450")` |
| Composables 5 Dirs | 104 symbols | `analyze(operation:"communities", id:"community-82")` |

<!-- gortex:communities:end -->
