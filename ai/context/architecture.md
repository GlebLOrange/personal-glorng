# Repository architecture (harness map)

```
personal-glorng/
├── client/          Vue 3 SPA
├── server/          FastAPI app package `app`
├── nginx/           Reverse proxy configs
├── docker-compose*.yml
├── docs/            VitePress handbook
├── deploy/
├── scripts/
├── .cursor/         Cursor rules, skills, agents, MCP (Gortex)
└── ai/              Harness context & workflows (this tree)
```

**API surface:** Treat OpenAPI under `/api/docs` and existing route contracts as stable unless the task explicitly allows API changes.

**Dev default:** lite mode — see `AGENTS.md` (`make dev-lite`, `make dev-lite-client`).

For deep dives, prefer Gortex trace/read on the subsystem under change rather than re-documenting modules here.
