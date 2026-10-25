# AGENTS.md

Dispatch only. Do not put bootstrap recipes, ports, or skill bodies here.

Shared entry for Cursor, Antigravity, and Claude. Skills and rules stay under [`.cursor/`](.cursor/); Antigravity and Claude reach them through [`.agents/`](.agents/) and [`.claude/`](.claude/) (symlinks and activation files).

| Before you… | Read |
|-------------|------|
| Edit application code | [`CODING_STANDARDS.md`](CODING_STANDARDS.md) |
| Set up env, run services, or run checks | [`docs/guide/getting-started.md`](docs/guide/getting-started.md), [`docs/guide/contributing.md`](docs/guide/contributing.md), [`README.md`](README.md) |
| Start a stack, back up, or maintain the DB | [`.cursor/commands/ops.md`](.cursor/commands/ops.md) (`/ops`) |
| Use Docker on a Cursor Cloud VM | [`docs/operations/cloud-vm.md`](docs/operations/cloud-vm.md) |

Personas: [`.cursor/agents/README.md`](.cursor/agents/README.md). Orchestration: [`.cursor/commands/task-loop.md`](.cursor/commands/task-loop.md).
