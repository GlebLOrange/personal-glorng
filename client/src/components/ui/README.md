# UI components

Shared primitives for the gLOrng client. Prefer these over one-off markup.

## Base* components (`BaseButton`, `BaseModal`, `BaseDrawer`, …)

Use for **interactive controls and overlays** in admin tools and feature UI.

- `BaseButton` — primary/secondary/ghost actions inside product screens
- `BaseModal` / `BaseDrawer` — dialogs and side panels (focus trap, Escape, focus restore built in)
- `BaseInput`, `BaseTextarea`, `BaseSelect` — forms; styling from `constants/formClasses.ts`
- `EmptyState` / `ErrorState` — list empty and fetch-error surfaces

Import explicitly per file (only `BaseImage` is global).

## Card system (`components/ui/card/`)

Use for **grouped content on a surface** — list items, settings sections, summary blocks.

- `Card`, `CardHeader`, `CardBody`, `CardTitle`, `CardActions`
- Variants: `default`, `compact`, `inset`, `ghost`
- Not a drop-in for every `div`; use when the block needs a border/background

## Marketing CTAs (`cta-primary`, `cta-secondary` in `main.css`)

Use on **portfolio/marketing pages** (hero, login, donations) where larger tap targets and gradient primary buttons match the brand.

Inside admin tools and dense product UI, prefer `BaseButton variant="primary"`.

## Async UI pattern

For data lists:

1. Skeleton rows while loading (`aria-busy="true"`)
2. `ErrorState` with optional retry for fetch failures (`role="alert"`)
3. `EmptyState` with title/description when the list is empty (`role="status"`)

See `NewsPage.vue` and `ExpenseList.vue` for reference implementations.

## Status colors

Semantic tokens in `@theme`: `status-error`, `status-warning`, `status-success`.

Use `text-status-*`, `alert-surface-error`, etc. — not raw Tailwind `red-400` / `amber-400`.

## URL-synced tabs

When tabs are shareable, sync with `router.replace({ query: { ...route.query, tab } })`.

Examples: `ExpensesTool` (`?tab=insights`), `TasksPage` (`?tab=sync`).
