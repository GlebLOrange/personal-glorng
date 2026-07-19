# UI components

Shared primitives for the gLOrng client. Prefer these over one-off markup.

## Base* components (`BaseButton`, `BaseModal`, `BaseDrawer`, …)

Use for **interactive controls and overlays** in admin tools and feature UI.

- `BaseButton` — primary/secondary/ghost actions; supports `loading` (`aria-busy` + disabled)
- `BaseModal` / `BaseDrawer` — dialogs and side panels (focus trap, Escape, focus restore built in)
- `BaseInput`, `BaseTextarea`, `BaseSelect` — forms; styling from `constants/formClasses.ts`
- Always pass a visible `label` prop (or an explicit `aria-label` when the label must be hidden)
- Optional `error` / `hint` wire `aria-invalid` + `aria-describedby`
- `EmptyState` / `ErrorState` — list empty and fetch-error surfaces
- `ListSkeleton` — shared loading skeleton (`aria-busy`); `AdminListSkeleton` wraps it for dense admin rows

Import explicitly per file (only `BaseImage` is global).

## Card system (`components/ui/card/`)

Use for **grouped content on a surface** — list items, settings sections, summary blocks.

- `Card`, `CardHeader`, `CardBody`, `CardTitle`, `CardActions`
- Variants: `default`, `compact`, `inset`, `ghost`, `dense`
- Radius is always `rounded-lg` (interactive token)
- Not a drop-in for every `div`; use when the block needs a border/background

## Marketing CTAs vs product buttons

**Marketing / portfolio surfaces** — use `cta-primary` and `cta-secondary` utilities from `main.css` on portfolio pages and donations. These use larger tap targets for brand moments.

**Auth and product UI** — prefer `BaseButton` (optionally with `loading`). Auth pages may use `cta-primary` / `cta-secondary` when matching marketing weight:

- `variant="primary"` — flat `accent-blue` fill (no gradient)
- `variant="secondary"` / `variant="ghost"` — neutral surfaces

Do not use `cta-primary` inside tool screens; do not add gradients to `BaseButton`.

## Async UI pattern

For data lists:

1. `ListSkeleton` (or `AdminListSkeleton`) while loading (`aria-busy="true"`)
2. `ErrorState` with optional retry for fetch failures (`role="alert"`)
3. `EmptyState` with title/description when the list is empty (`role="status"`)

See `NewsPage.vue` and `ExpenseList.vue` for reference implementations.

## Status colors

Semantic tokens in `@theme`: `status-error`, `status-warning`, `status-success`.

Use `text-status-*`, `alert-surface-error`, etc. — not raw Tailwind `red-400` / `amber-400`. Prefer `status-*` over legacy `accent-red` / `accent-amber` aliases.

## Overlay max-width naming

- `PageShell` `maxWidth`: `"xl"` | `"5xl"` both map to `max-w-5xl` (content column)
- `BaseModal` sizes: `"md"` | `"lg"` | `"2xl"`
- `BaseDrawer` sizes are independent (drawer panel width) — do not assume the same token means the same width as PageShell

## URL-synced tabs

When tabs are shareable, sync with `router.replace({ query: { ...route.query, tab } })`.

Examples: `ExpensesTool` (`?tab=insights`), `TasksPage` (`?tab=sync`).
