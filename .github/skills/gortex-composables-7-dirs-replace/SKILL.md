---
name: gortex-composables-7-dirs-replace
description: "Work in the composables +7 dirs · replace area — 157 symbols across 22 files (77% cohesion)"
---

# composables +7 dirs · replace

157 symbols | 22 files | 77% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `client/src/components/expenses/ExpenseDashboardPanel.vue`
- `client/src/components/layout/NavBar.vue`
- `client/src/composables/useApi.ts`
- `client/src/composables/useExpenseCalculator.ts`
- `client/src/composables/useExpenseFormMutations.ts`
- `client/src/composables/useExpensesTool.ts`
- `client/src/composables/useNewsSources.test.ts`
- `client/src/composables/useNewsSources.ts`
- `client/src/composables/useWeatherLocations.test.ts`
- `client/src/composables/useWeatherLocations.ts`
- `client/src/pages/CallbackPage.test.ts`
- `client/src/pages/ResetPasswordPage.test.ts`
- `client/src/pages/VerifyEmailPage.test.ts`
- `client/src/pages/admin/tools/ExpensesTool.vue`
- `client/src/utils/consumeQueryParams.ts`
- `client/src/utils/format.ts`
- `client/src/utils/goHome.ts`
- `client/src/utils/newsForms.ts`
- `client/src/utils/resumeShare.ts`
- `client/src/utils/weather.ts`
- `client/vite.config.ts`

## Key Files

| File | Symbols |
|------|---------|
| `` | split, toLowerCase, match, includes, replace, ... |
| `client/src/components/expenses/ExpenseDashboardPanel.vue` | focusEntry |
| `client/src/components/layout/NavBar.vue` | closeMobileMenu, handleGoHome |
| `client/src/composables/useApi.ts` | isAuthRefreshRequest, url |
| `client/src/composables/useExpenseCalculator.ts` | normalizeCalculatorMode, rest, applySumToBudget, switchMode, total, ... |
| `client/src/composables/useExpenseFormMutations.ts` | openSmartText |
| `client/src/composables/useExpensesTool.ts` | _panel, _panel, rest, value, resolvedPanel, ... |
| `client/src/composables/useNewsSources.test.ts` | replace |
| `client/src/composables/useNewsSources.ts` | closeDrawer, openCreate, blankForm |
| `client/src/composables/useWeatherLocations.test.ts` | query, isDefaultQuery |
| `client/src/composables/useWeatherLocations.ts` | query, normalized, setGuestDefaultByQuery |
| `client/src/pages/CallbackPage.test.ts` | raw, query, consumeQueryParams, useRouter, key, ... |
| `client/src/pages/ResetPasswordPage.test.ts` | useRouter |
| `client/src/pages/VerifyEmailPage.test.ts` | useRouter |
| `client/src/pages/admin/tools/ExpensesTool.vue` | focusAddFromInsights |
| `client/src/utils/consumeQueryParams.ts` | omitQueryKeys, query, key, keys, next, ... |
| `client/src/utils/format.ts` | title, title, cleaned, parts, formatBreadcrumbLabel, ... |
| `client/src/utils/goHome.ts` | router, goHome, scrollBehavior, hash, path |
| `client/src/utils/newsForms.ts` | withoutHostSourceMarker, sanitized, link, host, slug, ... |
| `client/src/utils/resumeShare.ts` | skillId, cleaned, label |
| `client/src/utils/weather.ts` | weatherConditionKind, weatherDesc, weatherIanaTimezone, timezone, WeatherConditionKind, ... |
| `client/vite.config.ts` | plugins.transformIndexHtml, html, output.manualChunks, fromEnv, hero, ... |

## Connected Communities

- **composables +5 dirs** (7 cross-edges)
- **composables +6 dirs** (5 cross-edges)
- **. +2 dirs · readLocalCurrency** (2 cross-edges)
- **composables +8 dirs** (2 cross-edges)
- **composables +4 dirs · useTasks** (2 cross-edges)
- **. +3 dirs · reloadCalendar** (1 cross-edges)
- **. +2 dirs · pickNativeAttrs** (1 cross-edges)
- **composables +2 dirs · sanitizeGuestWeatherLocations** (1 cross-edges)
- **composables +2 dirs · send** (1 cross-edges)
- **utils +1 dirs · parseUtcOffsetHours** (1 cross-edges)
- **utils +1 dirs · pathMatches** (1 cross-edges)
- **composables +2 dirs · isFinite** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-213")
explore(operation:"context", task:"understand composables +7 dirs · replace", format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
