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

Product chrome uses **three roles** from the Material sheet: primary wash, surface secondary/ghost, and error. Semantic names live in `constants/actionButtonVariants.ts`. Prefer **named actions** over raw HTTP families.

| User action | `BaseButton` `variant` | `action` on pill / icon / menu | Look |
|---|---|---|---|
| Create / Add / Primary | `create` / `add` / `primary` | `create` / `add` | Pale primary wash (`accent-coral` aliases `--color-primary`) |
| Save / submit / confirm | `save` (alias: `success`) | `save` | Same primary wash |
| Edit / update | `edit` | `edit` | Surface secondary (outline card) |
| Remove / delete | `delete` or `remove` | `delete` / `remove` | Pale error wash (`danger` prop = error legacy) |
| Cancel / dismiss | `cancel` | `cancel` | Ghost (muted until hover) |
| Neutral (OAuth, unlink, promote) | `secondary` | — (or explicit `family` for HTTP tabs) | Grayscale surface |
| Tertiary / filter clear | `ghost` (+ optional `quiet`) | — | Muted until hover |

**Examples:** `variant="cancel"` + `variant="save"` in form footers; `action="create"` on `+ task` pills; `variant="delete"` on confirm dialogs with `danger`.

Auth login/register submits may stay `primary`. Marketing `cta-*` stays separate. Do not invent new hex colors.

HTTP **status badges** and log rows still use 1xx–5xx families (`status-success`, `status-warning`, …). Legacy `accent-red` / `accent-amber` map to error / warning.

## Marketing CTAs vs product buttons vs toolbar pills

Three intentional systems — pick one per surface, do not mix adjacent CTAs:

| System | Where | Look |
|---|---|---|
| `cta-primary` / `cta-secondary` | Portfolio, donations, marketing moments | Pale 1xx wash / grayscale secondary (`main.css`) |
| `BaseButton` | Auth, forms, product dialogs, list rows | Pale HTTP-family wash; `secondary` grayscale |
| `ToolbarPillButton` / `IconActionButton` / `BaseDropdownMenu` | Admin toolbars, icon chrome, edit menus | Prefer `action="create"` / `save` / `edit` / `delete`; raw `family` only for HTTP-literal tabs (e.g. `AdminTabBar`) |

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

Wash recipe (idle → hover/selected → active): fill `/10` → `/12` + border `/22` → active `/14`; labels `text-*/88` (`ACTION_BUTTON_PAINT` in `httpStatusColors.ts`). Primary / `cta-primary` use the same pale primary wash. Icon clear/edit/remove/copy use `transparentIdle`. Do **not** re-add `min-h-10` / `h-10` / `!bg-*` / one-off hover colors on these primitives — use `variant`, `action`, `family`, `quiet`, `transparentIdle`, and `selected`. Size tokens live in `constants/formClasses.ts` (`CONTROL_BUTTON_*`).

**Text links** — use the `text-link` utility (primary ink + underline on hover/focus). Do not paint every `<a>` (tiles, nav, breadcrumbs stay undecorated).

**Marketing vs product accents** — portfolio/marketing may use `accent-violet` (tertiary), `accent-golden`, and `.accent-gradient` on brand name moments. Product and admin chrome uses **primary + surfaces + error** — tertiary/custom only on labeled pills/chips (`section-label-pill--*`, CV/news chips).

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

Canonical tokens live in `client/src/styles/main.css` as dual-theme CSS variables (`html[data-theme="dark"|"light"]`). Class names stay the same; values switch with theme. **Preference** is **dark** or **light** only (default dark); toggle: nav chrome flips dark ↔ light (`useColorTheme`, key `glorng-color-theme`). Legacy `system` values migrate once to the current OS theme.

**Surfaces:** `surface-dark` = page, `surface-card` = elevated, `surface-border` = borders, `surface-grid` = container-low, `surface-light` = primary text, `surface-sage` / `surface-mid` / `surface-muted` = body → secondary → muted.

**Roles (sheet):** `primary` / `on-primary` / `primary-container` for chrome. `accent-coral` and `accent-lavender` **alias primary**. `tertiary` (`accent-violet`) and `custom` (`status-cyan`) for pills/chips. `error` for destructive. Secondary **controls** stay surface+outline (sheet secondary fill matches primary).

| Role | Token | Dark | Light |
|---|---|---|---|
| Primary | `primary` / `accent-coral` | `#cfbdfe` | `#63588d` |
| On primary | `on-primary` / `on-accent` | `#1e1545` | `#ffffff` |
| Primary container | `primary-container` | `#4b4073` | `#cfc6e7` |
| Tertiary | `tertiary` / `accent-violet` | `#ffb1c8` | `#8d4b60` |
| Error | `status-error` | `#ffb4ab` | `#bf1c1e` |
| Custom | `custom` / `status-cyan` | `#8dceed` | `#23648a` |
| Success (status only) | `status-success` | `#a8d08d` | `#3b6d11` |
| Warning (status only) | `status-warning` | `#e8c468` | `#8b6914` |
| Page bg | `surface-dark` | `#141218` | `#fef7ff` |
| Card | `surface-card` | `#1d1b20` | `#f2ecf4` |
| Primary text | `surface-light` | `#e6e1e5` | `#1d1b20` |

Use `text-status-*`, `alert-surface-error`, `alert-surface-warning`, etc. — not raw Tailwind `red-400` / `amber-400`. Product button wash: idle `/10`, hover `/12` + border `/22`. Never invent one-off hex in components.

Typography: IBM Plex Sans; use `font-data` for status codes, counts, and money.

## Overlay max-width naming

- `PageShell` `maxWidth`: `"sm"` | `"md"` | `"5xl"` (`"5xl"` → `max-w-5xl` content column)
- `BaseModal` sizes: `"md"` | `"lg"` | `"2xl"`
- `BaseDrawer` sizes are independent (drawer panel width) — do not assume the same token means the same width as PageShell

## URL-synced tabs

When tabs are shareable, sync with `router.replace({ query: { ...route.query, tab } })`.

Examples: `ExpensesTool` (`?tab=expenses`), `TasksPage` (`?tab=sync`).

## PageShell body width

Use `body-width` on `PageShell` / `AdminPageLayout`: `full` (stretch), `content` (2-of-3 tile column), `column` (centred ~750px tool/settings panel). Prefer this over the deprecated `narrow` and `tool` props.
