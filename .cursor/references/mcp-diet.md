# MCP diet + Gortex snippet preference

Every enabled MCP server adds tool names (and on-demand schemas) to each request. Keep the set small per project.

## Expected servers for this repo

| Server | Status | Why |
|---|---|---|
| Gortex | **Primary** | Code graph: `search`, ranged `read`, `relations`, `trace`, `change` |
| Sentry / GitHub / others | Optional | Enable only for the task that needs them; disable otherwise in Cursor → MCP |

Do not edit `~/.cursor/mcp.json` from the repo; toggle servers in Cursor settings per project.

## Snippets over files

1. `search` → symbol/range hits; then `read` with a range, not the whole file.
2. `relations` / `trace` for callers/callees instead of opening every file.
3. Whole-file Read only when editing most of the file or Gortex is unavailable.
4. Large tool outputs: let Cursor spill to files; keep MCP replies lean.

## Prefer a Gortex-only profile
When a task only needs code navigation, run with Gortex as the sole enabled MCP server (toggle others off in Cursor Settings → MCP for the session); re-enable extras only when a task calls them. Tool schemas cost tokens every request — fewer servers, smaller prefix. Do not commit edits to `~/.cursor/mcp.json`.
