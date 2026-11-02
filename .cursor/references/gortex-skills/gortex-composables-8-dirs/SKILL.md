---
name: gortex-composables-8-dirs
description: "Work in the composables +8 dirs area — 124 symbols across 16 files (79% cohesion)"
---

# composables +8 dirs

124 symbols | 16 files | 79% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `client/src/App.test.ts`
- `client/src/components/tools/ToolTileGrid.test.ts`
- `client/src/components/tools/ToolTileGrid.vue`
- `client/src/components/ui/fieldA11y.ts`
- `client/src/composables/adminToolHarness.test.ts`
- `client/src/composables/useClipboard.ts`
- `client/src/composables/useDataExtractTool.ts`
- `client/src/composables/useNewsSources.ts`
- `client/src/pages/LoginPage.test.ts`
- `client/src/platform/services.ts`
- `client/src/types/index.ts`
- `client/src/utils/resumeGlance.ts`
- `client/src/utils/resumeShare.ts`
- `client/src/utils/shellHero.ts`
- `client/src/utils/toolsPageGroups.ts`

## Key Files

| File | Symbols |
|------|---------|
| `` | push, keys, isArray, sort, every |
| `client/src/App.test.ts` | path, router, mountApp |
| `client/src/components/tools/ToolTileGrid.test.ts` | service, overrides |
| `client/src/components/tools/ToolTileGrid.vue` | showAdminDemoChip, showSectionHeading, tool, ToolTileSection, section |
| `client/src/components/ui/fieldA11y.ts` | buildFieldDescribedBy, ids |
| `client/src/composables/adminToolHarness.test.ts` | useNotify |
| `client/src/composables/useClipboard.ts` | toast, copied, useClipboard |
| `client/src/composables/useDataExtractTool.ts` | selectedFile, profileChoice, batch, batchLabel, canPromoteSelected, ... |
| `client/src/composables/useNewsSources.ts` | source, sourceMeta, parts, host |
| `client/src/pages/LoginPage.test.ts` | useRouter |
| `client/src/platform/services.ts` | service, section, grouped, svc, grouped, ... |
| `client/src/types/index.ts` | ResumeProfileSelection, Education, Certification, SpokenLanguage, ResumeData, ... |
| `client/src/utils/resumeGlance.ts` | buildGlanceStats, stats, shipped, resume, GlanceStat, ... |
| `client/src/utils/resumeShare.ts` | selection, key, cleaned, ShareProfileSelection, values, ... |
| `client/src/utils/shellHero.ts` | escapeHtml, parts, resume, text, tagline, ... |
| `client/src/utils/toolsPageGroups.ts` | group, toolsPageGroupForSlug, list, grouped, ToolsPageGroupId, ... |

## Connected Communities

- **composables +6 dirs** (5 cross-edges)
- **composables +5 dirs** (4 cross-edges)
- **composables +4 dirs · useTasks** (4 cross-edges)
- **composables +2 dirs · uniqueCategoryNames** (1 cross-edges)
- **composables +7 dirs · replace** (1 cross-edges)
- **composables +4 dirs · run** (1 cross-edges)
- **. +2 dirs · downloadResult** (1 cross-edges)
- **components/ui +29 dirs** (1 cross-edges)
- **. +3 dirs · reloadCalendar** (1 cross-edges)
- **utils +1 dirs · parseUtcOffsetHours** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-76")
explore(operation:"context", task:"understand composables +8 dirs", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
