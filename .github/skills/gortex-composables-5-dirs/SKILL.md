---
name: gortex-composables-5-dirs
description: "Work in the composables +5 dirs area — 104 symbols across 10 files (73% cohesion)"
---

# composables +5 dirs

104 symbols | 10 files | 73% cohesion

## When to Use

Use this skill when working on files in:
- ``
- `client/src/components/charts/chartTheme.ts`
- `client/src/components/expenses/ExpenseLayout.test.ts`
- `client/src/composables/useExpenseCalculator.ts`
- `client/src/composables/useExpenseSummary.ts`
- `client/src/composables/useNewsAdmin.ts`
- `client/src/types/index.ts`
- `client/src/utils/format.ts`
- `client/src/utils/guestUrlShortener.ts`
- `client/src/utils/resumeGlance.ts`

## Key Files

| File | Symbols |
|------|---------|
| `` | slice, toFixed, reduce, map |
| `client/src/components/charts/chartTheme.ts` | colors, ChartTheme, name, fallback, cssVar, ... |
| `client/src/components/expenses/ExpenseLayout.test.ts` | props.formatExpenseDate, iso, iso, props.formatExpenseDate |
| `client/src/composables/useExpenseCalculator.ts` | whatIfCategoryId, activeMode, saving, toPayload, loadingState, ... |
| `client/src/composables/useExpenseSummary.ts` | useExpenseSummary, top, listLoading, topDescriptionChart, doughnutChart, ... |
| `client/src/composables/useNewsAdmin.ts` | formFromArticle, article |
| `client/src/types/index.ts` | ExpenseMonthTotal, ExpenseSummary, ExpenseCategoryTotal, ExpenseToolTotal |
| `client/src/utils/format.ts` | maxLen, formatBytes, cleaned, slug, bytes, ... |
| `client/src/utils/guestUrlShortener.ts` | title, id, items, trimmed, updateGuestShortUrlTitle |
| `client/src/utils/resumeGlance.ts` | countSkills, skills |

## Entry Points

- `client/src/composables/useExpenseCalculator.ts::useExpenseCalculator`

## Connected Communities

- **composables +4 dirs · useTasks** (10 cross-edges)
- **composables +6 dirs** (3 cross-edges)
- **composables +7 dirs · replace** (3 cross-edges)
- **composables · applyPayload** (3 cross-edges)
- **composables +2 dirs · isFinite** (1 cross-edges)
- **composables +2 dirs · useExpenseTransactions** (1 cross-edges)

## How to Explore

```
analyze(operation:"communities", id:"community-82")
explore(operation:"context", task:"understand composables +5 dirs", format:"gcx")
relations(operation:"usages", target:{symbol:"client/src/composables/useExpenseCalculator.ts::useExpenseCalculator"}, format:"gcx")
```

_`format: "gcx"` returns the [GCX1 compact wire format](../../docs/wire-format.md) — round-trippable, ~27% fewer tokens than JSON. Drop it for JSON output; agents using `@gortex/wire` or the Go `github.com/gortexhq/gcx-go` package decode either._
