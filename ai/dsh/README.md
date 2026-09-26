# DeepSeek Harness beside personal-glorng

DSH runs **outside** `server/` and `client/`. This folder holds profile patches and helpers only.

## Prerequisites

- Node.js 24+ (see root `.nvmrc`)
- `DEEPSEEK_API_KEY` in the environment (never commit)
- [`gortex`](https://github.com/) on `PATH`, daemon running when using `--proxy` (same as Cursor `.cursor/mcp.json`)
- Optional: copy [`../dsh.env.example`](../dsh.env.example) to a local env file outside git

## Gortex MCP (stdio)

[`run-gortex-mcp.sh`](run-gortex-mcp.sh) starts Gortex with the repo indexed. Paths are resolved from the script location so they work on macOS and Linux.

## Boot web UI with Gortex tools

From the repository root:

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
