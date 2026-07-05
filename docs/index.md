# gLOrng documentation

**gLOrng** is a FastAPI + Vue 3 developer portfolio and personal platform. The same domain services power the public site, admin panel, Telegram todobot, and background workers.

## Quick links

| Section | Topics |
|---------|--------|
| [Guide](/guide/getting-started) | Setup, architecture, dev workflow, frontend, contributing |
| [Operations](/operations/deployment) | Production deploy, database, backups, Cloudflare |
| [Reference](/reference/platform) | API catalog, Postman, env vars, security, testing, automation |

## Browse locally

```bash
make docs-dev    # http://localhost:5173
make docs-build  # static output in docs/.vitepress/dist
```

## Repository layout

```
server/    FastAPI backend (:8000)
client/    Vue 3 frontend (:3000)
nginx/     Reverse proxy (:80)
docs/      This handbook (VitePress)
```

For Cursor agents and cloud VM bootstrap, see [AGENTS.md](https://github.com/GlebLOrange/portfolio-glorng/blob/main/AGENTS.md) in the repo root.
