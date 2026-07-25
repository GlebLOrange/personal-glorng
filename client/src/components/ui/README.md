# UI components

Shared primitives for the gLOrng client. Prefer these over one-off markup.

## Base* components (`BaseButton`, `BaseModal`, `BaseDrawer`, …)

Use for **interactive controls and overlays** in admin tools and feature UI.

- `BaseButton` — primary/secondary/ghost/success actions; supports `loading` (`aria-busy` + disabled)
- `BaseModal` / `BaseDrawer` — dialogs and side panels (focus trap, Escape, focus restore built in)
- `BaseInput`, `BaseTextarea`, `BaseSelect` — forms; styling from `constants/formClasses.ts`
- Always pass a visible `label` prop (or an explicit `aria-label` when the label must be hidden)
- Optional `error` / `hint` wire `aria-invalid` + `aria-describedby`
- `EmptyState` / `ErrorState` — list empty and fetch-error surfaces
- `ListSkeleton` — shared loading skeleton (`aria-busy`); `AdminListSkeleton` wraps it for dense admin rows

Import explicitly per file (only `BaseImage` is global).

### Button action colors

Use existing palette tokens — map API action to variant:

| Action | Variant | Token |
|---|---|---|
| Create / add | `primary` | `accent-blue` wash |
| Save / update / send | `success` | `status-success` wash |
| Secondary / cancel (non-destructive) | `secondary` | grayscale (`surface-light`) |
| Quiet chrome / tertiary | `ghost` (+ optional `quiet`) | muted until hover accent |
| Cancel / delete / remove | `ghost` + `danger` (or `secondary` + `danger`) | `status-error` |

Auth submits and marketing `cta-*` stay blue/neutral; do not invent new hex colors.

## Marketing CTAs vs product buttons vs toolbar pills

Three intentional systems — pick one per surface, do not mix adjacent CTAs:

| System | Where | Look |
|---|---|---|
| `cta-primary` / `cta-secondary` | Portfolio, donations, marketing moments | Solid brand taps (`main.css`) |
| `BaseButton` | Auth, forms, product dialogs, list rows | Borderless wash; `primary` accent, `secondary` grayscale |
| `ToolbarPillButton` | Admin list toolbars, tool option bars, HTTP-ish families | Compact pills (`1xx` blue, `2xx` green submit, …) |

**Do not** use `cta-primary` inside tool screens; **do not** add gradients to `BaseButton`. Prefer `ToolbarPillButton` for admin toolbar primary actions and `BaseButton` for form/dialog actions.

**Marketing vs product accents** — portfolio/marketing pages may use `accent-blue`, `accent-violet`, `accent-golden`, and `.accent-gradient` on brand name moments. Product and admin UI stays single `accent-blue`; no decorative gradients on buttons.

## Card system (`components/ui/card/`)

Use for **grouped content on a surface** — list items, settings sections, summary blocks.

- `Card`, `CardHeader`, `CardBody`, `CardTitle`, `CardActions`
- Variants: `default`, `compact`, `inset`, `ghost`, `dense`
- Radius is always `rounded-lg` (interactive token)
- Not a drop-in for every `div`; use when the block needs a border/background

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
