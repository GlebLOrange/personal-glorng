# Spec: `agy-ai-tool` — proposed (not in tree)

**Status:** Proposed only. This slug exists in this handbook page and nowhere else in the repo.

## Current state

| Check | Result |
|-------|--------|
| `server/app/platform/registry.py` | No `agy-ai-tool` service |
| FastAPI routers / OpenAPI | No `/api/tools/agy-ai-tool` routes |
| Vue client routes / tools pages | No `/tools/agy-ai-tool` page |
| Tests | No `test_agy_ai_tool` / `AgyAiTool` coverage |

Nothing in this file is a shipped API, UX, or registry contract. Do not treat modes, endpoints, rate limits, or registry snippets below any older draft as implemented.

## Intent (backlog idea only)

A public developer workbench that could convert or explain SQL→Mongo aggregations, cURL→SDK snippets, and regex/cron patterns — aligned with the portfolio stack (Motor, FastAPI, TypeScript). That product is **not** built yet.

## Next steps (if productized later)

1. Add a real registry entry, router, and client route under a dedicated TASK.
2. Refresh catalogs with `make docs-generate`.
3. Replace this page with a current-state status that matches the tree.

## Related

- Shipped tools catalog: [Platform overview](/reference/platform), [API endpoints (generated)](/generated/api-endpoints)
- Existing AI surfaces: admin `ai-chat` / public search chat (feature-flagged via Settings)
