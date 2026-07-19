# gLOrng documentation

**gLOrng** is a FastAPI + Vue 3 developer portfolio and personal platform. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Quick links

| Section | Topics |
|---------|--------|
| [Guide](/guide/getting-started) | Setup, architecture, dev workflow, frontend, contributing |
| [Operations](/operations/deployment) | Production deploy, database, backups, Cloudflare |
| [Reference](/reference/platform) | API catalog, Postman, env vars, security, testing, automation |
| [ADRs](/adr/) | Architecture decision records |
| [API endpoints](/generated/api-endpoints) | Generated OpenAPI path table |
| [Architecture inventory](/generated/architecture-inventory) | Generated platform + Compose inventory |

Published site: [gleblorange.github.io/portfolio-glorng](https://gleblorange.github.io/portfolio-glorng/) (GitHub Pages via Actions).

## Browse locally

```bash
make docs-generate   # OpenAPI + architecture inventory into docs/generated/
make docs-dev        # http://localhost:5173 (runs generate first)
make docs-build      # static output in docs/.vitepress/dist
```

## Repository layout

```
server/    FastAPI backend (:8000)
client/    Vue 3 frontend (:3000)
nginx/     Reverse proxy (:80)
docs/      This handbook (VitePress)
```

For Cursor agents and cloud VM bootstrap, see [AGENTS.md](https://github.com/GlebLOrange/portfolio-glorng/blob/main/AGENTS.md) in the repo root.
