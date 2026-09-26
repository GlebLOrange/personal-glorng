# UI components

Shared primitives for the Gleb.Y client. Prefer these over one-off markup.

## Base* components (`BaseButton`, `BaseModal`, `BaseDrawer`, …)

Use for **interactive controls and overlays** in admin tools and feature UI.

- `BaseButton` — primary/secondary/ghost/success actions; supports `loading` (`aria-busy` + disabled)
- `BaseModal` / `BaseDrawer` — dialogs and side panels (focus trap, Escape, focus restore built in)
- `BaseInput`, `BaseTextarea`, `BaseSelect` — forms; styling from `constants/formClasses.ts`
- Always pass a visible `label` prop (or an explicit `aria-label` / `ariaLabel` when the label must be hidden). `IconActionButton` requires `ariaLabel` (use `aria-label` in templates).
- Shell `placeholder` is an **in-bar overlay tip** (aria-hidden): visible only when empty, including while focused; never the accessible name — pass `label` or `aria-label`
- `SearchInput` — same overlay pattern with a leading search icon; clear X slot is always reserved (invisible when empty) so text does not shift
- Optional `error` / `hint` wire `aria-invalid` + `aria-describedby`
- `EmptyState` / `ErrorState` — list empty and fetch-error surfaces
- `ListSkeleton` — shared loading skeleton (`aria-busy`); `AdminListSkeleton` wraps it for dense admin rows

Import explicitly per file (only `BaseImage` is global).

### Button action colors (standard)

Semantic names live in `constants/actionButtonVariants.ts` (`SEMANTIC_ACTION_HTTP_FAMILY`). Prefer **named actions** over raw HTTP families so create/save/cancel stay consistent.

| User action | `BaseButton` `variant` | `ToolbarPillButton` `action` | HTTP family | Look |
|---|---|---|---|---|
| Create | `create` | `create` | 1xx | Solid `accent-blue` (same as `primary`) |
| Add | `add` | `add` | 1xx | Solid `accent-blue` |
| Save / submit / confirm | `save` (alias: `success`) | `save` | 2xx | Pale green wash |
| Edit / update | `edit` | `edit` | 3xx | Pale gold wash |
| Remove / delete | `delete` or `remove` | `delete` / `remove` | 4xx | Pale rose wash (`danger` prop = 4xx legacy) |
| Cancel / dismiss | `cancel` | `cancel` | 5xx | Pink–red wash |
| Neutral (OAuth, unlink, promote) | `secondary` | — (or explicit `family`) | — | Grayscale |
| Tertiary / filter clear | `ghost` (+ optional `quiet`) | — | — | Muted until hover |

**Examples:** `variant="cancel"` + `variant="save"` in form footers; `action="create"` on `+ task` pills; `variant="delete"` on confirm dialogs with `danger`.

Auth login/register submits may stay `primary`. Marketing `cta-*` stays separate. Do not invent new hex colors.

`status-warning` is the 3xx family. Legacy `accent-red` / `accent-amber` map to error / warning.

## Marketing CTAs vs product buttons vs toolbar pills

Three intentional systems — pick one per surface, do not mix adjacent CTAs:

| System | Where | Look |
|---|---|---|
| `cta-primary` / `cta-secondary` | Portfolio, donations, marketing moments | Pale 1xx / 3xx washes (`main.css`, same paint as product) |
| `BaseButton` | Auth, forms, product dialogs, list rows | Pale HTTP-family wash; `secondary` grayscale |
| `ToolbarPillButton` | Admin list toolbars, tool option bars | Prefer `action="create"` / `save` / `delete`; use raw `family` only for HTTP-literal UI (filters, pause, cook) |

**Do not** use `cta-primary` inside tool screens; **do not** add gradients to `BaseButton`. Prefer `ToolbarPillButton` for admin toolbar primary actions and `BaseButton` for form/dialog actions.

### Action copy (no bare `+`)

Product `BaseButton` / `ToolbarPillButton` labels must name the action with a short noun: `+ task`, `+ recipe`, `+ expense`. A lone `+` (or other single glyph) is banned. Icon-only chrome (`IconActionButton`, nav theme toggle) remains allowed when it has an `aria-label`.

### Control sizing (do not override)

| Control | Default height | Notes |
|---|---|---|
| `BaseButton` `sm` / `md` / `field` | **h-10** | `sm` only tightens `px`/`text` — it is **not** shorter |
| `BaseButton` `lg` | **h-12** | Keypad exception (`CalculatorTool`) only |
| `BaseButton` `icon` | **h-10 w-10** | Prefer `IconActionButton` in tools |
| `ToolbarPillButton` | **h-10 px-4** | No size prop — do not add `min-h-10` |
| `IconActionButton` (+ wrappers) | **h-10 w-10** | Icon-only chrome; in-field clear uses `size="field"` (same square) |
| `BaseSelect` | **h-10** (`compact` → h-9) | Dense toolbars only for compact |

Wash recipe (idle → hover/selected → active): fill `/10` → `/12` + border `/22` → active `/14`; labels `text-*/88` (`ACTION_BUTTON_PAINT` in `httpStatusColors.ts`). Primary / `cta-primary` use the same pale 1xx wash. Icon clear/edit/remove/copy use `transparentIdle`. Do **not** re-add `min-h-10` / `h-10` / `!bg-*` / one-off hover colors on these primitives — use `variant`, `action`, `family`, `quiet`, `transparentIdle`, and `selected`. Size tokens live in `constants/formClasses.ts` (`CONTROL_BUTTON_*`).

**Marketing vs product accents** — portfolio/marketing pages may use `accent-blue`, `accent-violet`, `accent-golden`, and `.accent-gradient` on brand name moments. Product and admin UI uses only the **1xx–5xx** pale set + surfaces — no golden/violet on tools, chips, or product buttons.

## Card system (`components/ui/card/`)

Use for **grouped content on a surface** — list items, settings sections, summary blocks.

- `Card`, `CardHeader`, `CardBody`, `CardTitle`
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

Canonical tokens live in `client/src/styles/main.css` as pale dual-theme CSS variables (`html[data-theme="dark"|"light"]`). Class names stay the same; values switch with theme. **Preference** is **dark** or **light** only (default dark); toggle: nav chrome flips dark ↔ light (`useColorTheme`, key `glorng-color-theme`). Legacy `system` values migrate once to the current OS theme.

**Roles (both themes):** `surface-dark` = page background, `surface-card` = elevated surface, `surface-border` = borders, `surface-light` = primary text, `surface-sage` / `surface-mid` / `surface-muted` = body → secondary → muted. `on-accent` = dark ink on solid pale CTA fills. Product/admin uses pale 1xx–5xx + surfaces only; violet/golden are marketing-only.

| Family | Token | Dark (resolved) | Light |
|---|---|---|---|
| 1xx | `accent-blue` | `#8ec4e0` | `#7aa3d4` |
| 2xx | `status-success` | `#7bc49a` | `#86c9a0` |
| 3xx | `status-warning` | `#d4ce94` | `#d4b86a` |
| 4xx | `status-error` | `#e88a8a` | `#e08a8a` |
| 5xx | `status-critical` | `#d98aad` | `#d98aad` |
| Page bg | `surface-dark` | `#111827` | `#e5e7eb` |
| Primary text | `surface-light` | `#f9f9fb` | `#111827` |

Use `text-status-*`, `alert-surface-error`, `alert-surface-warning` (pale yellow), etc. — not raw Tailwind `red-400` / `amber-400`. Wash pattern: idle `/3`, hover/selected `/15` + border `/40`. Never use saturated sheet hexes as solid button fills.

Typography: IBM Plex Sans; use `font-data` for status codes, counts, and money.

## Overlay max-width naming

- `PageShell` `maxWidth`: `"xl"` | `"5xl"` both map to `max-w-5xl` (content column)
- `BaseModal` sizes: `"md"` | `"lg"` | `"2xl"`
- `BaseDrawer` sizes are independent (drawer panel width) — do not assume the same token means the same width as PageShell

## URL-synced tabs

When tabs are shareable, sync with `router.replace({ query: { ...route.query, tab } })`.

Examples: `ExpensesTool` (`?tab=expenses`), `TasksPage` (`?tab=sync`).
