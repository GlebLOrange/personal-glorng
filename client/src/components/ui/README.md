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

Use the pale **1xx–5xx** family tokens — map API action to variant:

| Action | Family | Variant / control | Token |
|---|---|---|---|
| Create / add / primary / info | 1xx | `BaseButton` `primary`, `ToolbarPillButton` `1xx` | `accent-blue` wash |
| Save / success / created | 2xx | `BaseButton` `success`, pill `2xx` | `status-success` wash |
| Update / redirect / caution | 3xx | pill `3xx`, edit chrome | `status-warning` wash |
| Delete / client error | 4xx | `danger`, pill `4xx` | `status-error` |
| Critical / server error | 5xx | pill `5xx`, critical badges | `status-critical` |
| Secondary / cancel (non-destructive) | — | `secondary` | grayscale (`surface-light`) |
| Quiet chrome / tertiary | — | `ghost` (+ optional `quiet`) | muted until hover accent |

`status-warning` is the 3xx family (pale yellow). Prefer `status-warning` for edit/pending/caution; leave `status-cyan` for legacy callouts only. Legacy `accent-red` / `accent-amber` map to error / warning.

Auth submits and marketing `cta-*` stay blue/neutral; do not invent new hex colors.

## Marketing CTAs vs product buttons vs toolbar pills

Three intentional systems — pick one per surface, do not mix adjacent CTAs:

| System | Where | Look |
|---|---|---|
| `cta-primary` / `cta-secondary` | Portfolio, donations, marketing moments | Solid brand taps (`main.css`) |
| `BaseButton` | Auth, forms, product dialogs, list rows | Borderless wash; `primary` accent, `secondary` grayscale |
| `ToolbarPillButton` | Admin list toolbars, tool option bars, HTTP-ish families | Compact pills (`1xx` blue, `2xx` green submit, …) |

**Do not** use `cta-primary` inside tool screens; **do not** add gradients to `BaseButton`. Prefer `ToolbarPillButton` for admin toolbar primary actions and `BaseButton` for form/dialog actions.

### Control sizing (do not override)

| Control | Default height | Notes |
|---|---|---|
| `BaseButton` `sm` / `md` / `field` | **h-11** | `sm` only tightens `px`/`text` — it is **not** shorter |
| `BaseButton` `lg` | **h-12** | Keypad exception (`CalculatorTool`) only |
| `BaseButton` `icon` | **h-8 w-8** | Prefer `IconActionButton` in tools |
| `ToolbarPillButton` | **h-11 px-4** | No size prop — do not add `min-h-11` |
| `IconActionButton` (+ wrappers) | **h-8 w-8** | Icon-only chrome |
| `BaseSelect` | **h-11** (`compact` → h-9) | Dense toolbars only for compact |

Wash recipe (idle → hover/selected → active): `/3` → `/15` + border `/40` → `/25`. Do **not** re-add `min-h-11` / `h-11` / `!bg-*` / one-off hover colors on these primitives — use `variant`, `family`, `quiet`, and `selected`.

**Marketing vs product accents** — portfolio/marketing pages may use `accent-blue`, `accent-violet`, `accent-golden`, and `.accent-gradient` on brand name moments. Product and admin UI uses only the **1xx–5xx** pale set + surfaces — no golden/violet on tools, chips, or product buttons.

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

## Status / palette colors

Canonical tokens live in `client/src/styles/main.css` as pale dual-theme CSS variables (`html[data-theme="dark"|"light"]`). Class names stay the same; values switch with theme. Default is **dark**. Toggle: nav chrome cycles dark → light → system (`useColorTheme`, key `glorng-color-theme`).

**Roles (both themes):** `surface-dark` = page background, `surface-card` = elevated surface, `surface-border` = borders, `surface-light` = primary text, `surface-sage` / `surface-mid` / `surface-muted` = body → secondary → muted. `on-accent` = dark ink on solid pale CTA fills. Product/admin uses pale 1xx–5xx + surfaces only; violet/golden are marketing-only.

| Family | Token | Dark (default) | Light |
|---|---|---|---|
| 1xx | `accent-blue` | `#8ec4e0` | `#7aa3d4` |
| 2xx | `status-success` | `#7bc49a` | `#86c9a0` |
| 3xx | `status-warning` | `#d4ce94` | `#d4b86a` |
| 4xx | `status-error` | `#e88a8a` | `#e08a8a` |
| 5xx | `status-critical` | `#d98aad` | `#d98aad` |
| Page bg | `surface-dark` | `#111827` | `#f9f9fb` |
| Primary text | `surface-light` | `#f9f9fb` | `#111827` |

Use `text-status-*`, `alert-surface-error`, `alert-surface-warning` (pale yellow), etc. — not raw Tailwind `red-400` / `amber-400`. Wash pattern: idle `/3`, hover/selected `/15` + border `/40`. Never use saturated sheet hexes as solid button fills.

Typography: IBM Plex Sans; use `font-data` for status codes, counts, and money.

## Overlay max-width naming

- `PageShell` `maxWidth`: `"xl"` | `"5xl"` both map to `max-w-5xl` (content column)
- `BaseModal` sizes: `"md"` | `"lg"` | `"2xl"`
- `BaseDrawer` sizes are independent (drawer panel width) — do not assume the same token means the same width as PageShell

## URL-synced tabs

When tabs are shareable, sync with `router.replace({ query: { ...route.query, tab } })`.

Examples: `ExpensesTool` (`?tab=insights`), `TasksPage` (`?tab=sync`).
