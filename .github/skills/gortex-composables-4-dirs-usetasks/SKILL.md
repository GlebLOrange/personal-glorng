---
name: gortex-composables-4-dirs-usetasks
description: "Work in the composables +4 dirs · useTasks area — 352 symbols across 22 files (87% cohesion)"
---

# composables +4 dirs · useTasks

352 symbols | 22 files | 87% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `client/src/composables/useAiChat.ts`
- `client/src/composables/useApiAction.ts`
- `client/src/composables/useCategoryManager.ts`
- `client/src/composables/useExpenseCategorySettings.ts`
- `client/src/composables/useExpenseFormMutations.ts`
- `client/src/composables/useHealthChecker.ts`
- `client/src/composables/useNews.ts`
- `client/src/composables/useNewsAdmin.ts`
- `client/src/composables/useNewsSources.test.ts`
- `client/src/composables/useNewsSources.ts`
- `client/src/composables/useNotify.ts`
- `client/src/composables/usePermissions.ts`
- `client/src/composables/useQrLibrary.ts`
- `client/src/composables/useRecipes.ts`
- `client/src/composables/useScrollListFingerprint.ts`
- `client/src/composables/useSearchChat.ts`
- `client/src/composables/useTasks.ts`
- `client/src/constants/search.ts`
- `client/src/pages/admin/AdminUsersPage.vue`
- `client/src/utils/resumeGlance.ts`
- `client/src/utils/scrollRestore.ts`

## Key Files

| File | Symbols |
|------|---------|
| `` | find |
| `client/src/composables/useAiChat.ts` | canSend, modelLabel, clear, toast, providerLabel, ... |
| `client/src/composables/useApiAction.ts` | lastError, useApiAction, loading, defaultOptions, toast |
| `client/src/composables/useCategoryManager.ts` | useCategoryManager, editingCategoryId, editingCategoryName, runApi, defaultCategoryName, ... |
| `client/src/composables/useExpenseCategorySettings.ts` | confirmDeleteCategory, replacement, category, ok |
| `client/src/composables/useExpenseFormMutations.ts` | options, deleteTargetId, quickAddAmountError, showForm, savingExpense, ... |
| `client/src/composables/useHealthChecker.ts` | selectedId, creating, newLabel, runHistory, newUrl, ... |
| `client/src/composables/useNews.ts` | countLabel, runDetail, total, runStats, listLoading, ... |
| `client/src/composables/useNewsAdmin.ts` | metadataRequestId, listError, listLoading, activeFilterLabel, loadSources, ... |
| `client/src/composables/useNewsSources.test.ts` | useRoute, useRouter |
| `client/src/composables/useNewsSources.ts` | hasActiveFilters, useNewsSources, runSave, runDelete, DEFAULT_ENABLED_FILTER, ... |
| `client/src/composables/useNotify.ts` | useNotify |
| `client/src/composables/usePermissions.ts` | capability, permissions, can, canAccess, canUseAdminHub, ... |
| `client/src/composables/useQrLibrary.ts` | useQrLibrary, runDelete, deleting, runList, canReadLibrary, ... |
| `client/src/composables/useRecipes.ts` | route, showForm, target, runDetail, recipeCountLabel, ... |
| `client/src/composables/useScrollListFingerprint.ts` | useScrollListFingerprint, getFingerprint, sync, route |
| `client/src/composables/useSearchChat.ts` | messages, UseSearchChatOptions, abortController, useSearchChat, input, ... |
| `client/src/composables/useTasks.ts` | runDetail, syncTotal, selectedTask, calendarTruncated, filterStatus, ... |
| `client/src/constants/search.ts` | raw, q, effectiveSearchQuery |
| `client/src/pages/admin/AdminUsersPage.vue` | loadUsers, user, data |
| `client/src/utils/resumeGlance.ts` | picks, backend, frontend, skills, primaryStack |
| `client/src/utils/scrollRestore.ts` | path, fingerprint, setScrollFingerprint |

## Entry Points

- `client/src/composables/useTasks.ts::useTasks`
- `client/src/composables/useRecipes.ts::useRecipes`

## Connected Communities

- **composables +7 dirs · replace** (7 cross-edges)
- **composables +2 dirs · openWriterEdit** (3 cross-edges)
- **composables +2 dirs · isFinite** (2 cross-edges)
- **composables +5 dirs** (2 cross-edges)
- **composables +7 dirs · toast** (2 cross-edges)
- **composables +2 dirs · useExpensesTool** (2 cross-edges)
- **composables +2 dirs · delete** (2 cross-edges)
- **composables +3 dirs · useActiveWeatherQuery** (2 cross-edges)
- **composables +2 dirs · uniqueCategoryNames** (1 cross-edges)
- **composables +6 dirs** (1 cross-edges)
- **composables +4 dirs · run** (1 cross-edges)
- **composables +1 dirs · NewsSource** (1 cross-edges)
- **composables +1 dirs · switchTab** (1 cross-edges)
- **utils · sanitizeGuestQrLibrary** (1 cross-edges)
- **composables +1 dirs · useChatConfig** (1 cross-edges)
- **composables +3 dirs · ensureDefaultLocation** (1 cross-edges)
- **composables +2 dirs · datetimeLocalValue** (1 cross-edges)
- **. +2 dirs · applyConsent** (1 cross-edges)
- **composables +1 dirs · filterAiChat** (1 cross-edges)
- **components/admin +1 dirs** (1 cross-edges)
- **composables +1 dirs · createGuestQr** (1 cross-edges)
- **composables · loadStats** (1 cross-edges)
- **. +3 dirs · reloadCalendar** (1 cross-edges)
- **composables +1 dirs · reloadAdminNews** (1 cross-edges)
- **composables +1 dirs · deleteSaved** (1 cross-edges)
- **composables · loadConfig** (1 cross-edges)
- **composables +2 dirs · close** (1 cross-edges)
- **composables +1 dirs · hydrateFromSourceUrl** (1 cross-edges)
- **composables · readStorage** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-119")
explore(operation:"context", task:"understand composables +4 dirs · useTasks", format:"gcx")
relations(operation:"usages", target:{symbol:"client/src/composables/useTasks.ts::useTasks"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
