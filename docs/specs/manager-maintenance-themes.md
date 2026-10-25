# Spec: Manager maintenance themes

## Objective

When the human asks for maintenance-shaped work, Manager recommends from this **seed map** (or Assigns one TASK). Manager never implements. Feature-shaped asks must not inject these themes.

## Seed map (current)

Inspect these anchors before recommending. Skip themes already clearly covered; do not invent greenfield systems.

| Theme | Anchors | What to look for |
|-------|---------|------------------|
| **Backups** | [`scripts/db_maintenance.sh`](../../scripts/db_maintenance.sh), [`docs/operations/backup-restore.md`](../operations/backup-restore.md), `make backup` / `make backup-install`, admin jobs `backup` / `stale` on `/admin/db-maintenance` | Offsite / `BACKUP_REQUIRE_OFFSITE`, restore drill, `LAST_SUCCESS` / stale-check gaps vs docs |
| **Sanitize** | [`server/app/core/text.py`](../../server/app/core/text.py), [`client/src/utils/sanitizeEmailHtml.ts`](../../client/src/utils/sanitizeEmailHtml.ts), [`server/app/core/xml_security.py`](../../server/app/core/xml_security.py), [`docs/reference/security.md`](../reference/security.md); agent preflight `/maintain` | Unsanitized `v-html`, missing validators on new inputs, XML/HTML trust boundaries |
| **Cleanup** | fileshare `cleanup_expired` + Celery `cleanup_expired_shares`, admin job `cleanup`, backup rotation, vid-download temp cleanup when untrusted tools are enabled | Expired shares/files left on disk, missing periodic jobs, incomplete rotation |
| **DRY** | Only when search finds duplicated logic; agent preflight `/maintain` | Scoped extract — not speculative “refactor everything” |
| **Seed / sync** | Admin jobs `seed` / `sync` on `/admin/db-maintenance`; CLI `make seed-db` | Seed gated in production unless `MAINTENANCE_SEED_ENABLED`; calendar sync batch ceilings |

## Decisions (locked)

| # | Decision | Choice |
|---|----------|--------|
| D1 | What to change | Manager **recommends** app maintenance themes |
| D2 | When to surface | **A** — maintenance-shaped asks only |
| D3 | Cap | Recommend ≤3; Assign exactly one TASK yaml when Mode Assign |
| D4 | Grounding | Paths/commands from Gortex/search (or git fallback); empty inventing forbidden |

## Out of scope

- Rewriting all personas for DRY
- Changing `/task-loop` flow
- Implementing backup/offsite/sanitize/cleanup app work in the same slice as guidance
- Extra backup copies of agent markdown (git is backup)
- Editing [`manager.md`](../../.cursor/agents/manager.md) or other personas from a docs-only pass

## Commands

```bash
make docs-build   # when this spec or handbook structure changes
```

## Boundaries

- **Always:** keep manager readonly; ≤3 Recommend; Assign only for implementation asks; ground in found paths; update this seed map when anchors move
- **Ask first:** expanding trigger beyond A; editing task-loop; adding deps or app maintenance implementations in a guidance-only PR
- **Never:** spawn personas from manager; invent graph results; recommend work already on `origin/main`; commit secrets

## Success criteria

1. This page’s seed map matches real paths/commands in the tree.
2. Manager persona (separately) stays trigger-gated (A) and points here rather than duplicating the map in README.
3. Shared [`.cursor/agents/README.md`](../../.cursor/agents/README.md) remains the requirement-bar source.
