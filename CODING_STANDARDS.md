# Coding standards

This file is a **router only**: it points agents and humans to canonical guidance in [`.cursor/skills/`](.cursor/skills/). Path-triggered stubs under [`.cursor/rules/`](.cursor/rules/) automatically load the relevant skill when you edit matching files — **do not copy skill content into this index**.

## Primary skills

| Topic | Skill |
|-------|-------|
| FastAPI / Python backend | [`python-fast-api`](.cursor/skills/python-fast-api/SKILL.md) |
| Vue 3 client | [`vue-client`](.cursor/skills/vue-client/SKILL.md) |
| Pinia state | [`vue-pinia`](.cursor/skills/vue-pinia/SKILL.md) |
| Dependencies | [`dependencies`](.cursor/skills/dependencies/SKILL.md) |
| Agent safety (commits, destructive ops) | [`agent-safety`](.cursor/skills/agent-safety/SKILL.md) |
| UI / design system | [`toss-style-design-system`](.cursor/skills/toss-style-design-system/SKILL.md) |

## Related

- [`client-server`](.cursor/skills/client-server/SKILL.md) — Vue ↔ FastAPI contract patterns
- [`agent-git-workflow`](.cursor/skills/agent-git-workflow/SKILL.md) — branch and commit conventions for agents
- [`ui-ux-pro-max`](.cursor/skills/ui-ux-pro-max/SKILL.md) — UX overview and recommendations

For environment bootstrap and Cloud VM operational details, see [`AGENTS.md`](AGENTS.md).
