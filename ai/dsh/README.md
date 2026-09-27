# DeepSeek Harness beside personal-glorng

DSH runs **outside** `server/` and `client/`. This folder holds profile patches and helpers only.

## Prerequisites

- Node.js 24+ (see root `.nvmrc`)
- `DEEPSEEK_API_KEY` in the environment (never commit)
- `gortex` on `PATH`, daemon running when using `--proxy` (same as Cursor `.cursor/mcp.json`)
- Optional: copy [`../dsh.env.example`](../dsh.env.example) to a local env file outside git

## Gortex MCP (stdio)

[`run-gortex-mcp.sh`](run-gortex-mcp.sh) starts `gortex mcp --proxy` against the already-running daemon. The daemon holds the repo index; the script does not pass `--index`.

## Boot web UI with Gortex tools

**Default:** `make dev` / `make dev-lite` starts DSH in the background on `http://127.0.0.1:3080` (and `make down` stops it). Set `DEEPSEEK_API_KEY` in the repo `.env` (or the environment) for chat; the UI still boots without it.

Foreground (logs in the terminal):

```bash
make dev-dsh
```

Manual equivalent from the repository root:

```bash
export PATH="$HOME/.nvm/versions/node/v24.18.0/bin:$PATH"   # adjust if needed
export DSH_HOME="${DSH_HOME:-$HOME/.dsh}"
export DEEPSEEK_API_KEY=...                                  # required for default model

npx @deepseek-ai/dsh web --patch ai/dsh/patch-gortex.yml
```

Inspect the composed profile without starting the server:

```bash
npx @deepseek-ai/dsh --profile web --patch ai/dsh/patch-gortex.yml --dump-config
```

After startup, Gortex tools appear as `mcp__gortex__*` (exact names depend on Gortex tool surface).

## Agent prompts

Load harness role briefs from [`../agents/`](../agents/) and project contract from [`../context/`](../context/). DSH system prompts should cite those files rather than duplicating `.cursor/` rules.

## Safety defaults

- Keep `DSH_PERMISSION_MODE=workspace-write` (DSH default) scoped to this repo checkout.
- Do not store production MongoDB/Redis/JWT secrets in DSH credential files for the pilot.
- No auto-merge; humans merge PRs on GitHub.
