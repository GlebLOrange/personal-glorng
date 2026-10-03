# Frontend CSS audit

Read-only audit of the production Vite bundle (March 2026). Regenerate numbers with:

```bash
cd client
VITE_PUBLIC_ORIGIN=https://ci.example.test npm run build
ls -la dist/assets/*.css
```

## Summary

| Asset | Raw (approx.) | Gzip (approx.) | Blocks first paint? |
|-------|---------------|----------------|---------------------|
| `index-*.css` (Tailwind + `main.css`) | ~123–126 KB | ~17 KB | **Yes** — linked from `index.html` |
| `cookieconsent-*.css` (library) | ~31 KB | ~9 KB | **No** — loaded with deferred consent chunk |
| `cookieconsent-theme.css` (app overrides) | &lt;1 KB | tiny | **No** — same chunk as consent |
| `latin-600-*.css` (font 600) | ~240 B | tiny | **No** — idle `requestIdleCallback` |
| Per-component CSS (e.g. `BaseInput-*.css`) | &lt;200 B each | tiny | With owning route chunk |

There is **no route-level CSS split** today: one global stylesheet covers portfolio, tools, and admin. That is acceptable for gzip (~17 KB) but the **raw** file is large because Tailwind emits utilities for the whole app surface.

## What drives `index-*.css`

1. **`client/src/styles/main.css`** — Tailwind 4 (`@import "tailwindcss"`), dual-theme CSS variables (`@theme` + light/dark palettes), many `@utility` tokens (page shell, CTAs, donation brands, nav links), portfolio print rules, admin list chrome, scrollbar helpers.
2. **Class usage across all Vue SFCs** — Tailwind scans `client/src/**/*.{vue,ts}`; admin and tool pages contribute utilities even when users only visit `/`.
3. **`httpStatusColors` / action variants** — used from `NavBar` and shared UI (entry-adjacent), so status-family colors stay in the global bundle by design.

## Already optimized

- **Chart.js** — not in entry JS/CSS preload (see `check-entry-preloads.mjs`).
- **Cookie consent library CSS** — separate async chunk; theme overrides moved to `cookieconsent-theme.css` (loaded with consent, not in `index-*.css`).
- **IBM Plex 600** — not in critical path (preload 400/700 in `index.html`; 600 loads idle).

## Recommendations (priority)

| Priority | Action | Effort | Impact |
|----------|--------|--------|--------|
| P2 | Keep **`check-css-budget.mjs`** in CI (`build:check`) — fails if `index-*.css` &gt; 132 KB raw | S | Prevents silent regressions |
| P2 | Run **`ANALYZE=true npm run build`** when adding large UI surfaces; inspect `dist/stats.html` | S | Find new utility blow-ups |
| P3 | **Optional second CSS entry** for admin-only `@utility` blocks (separate Vite input, import only from admin layout) | L | Moderate raw savings; more build complexity |
| P3 | **Public-only Tailwind `@source` scope** — risky; easy to purge classes used on public pages | M | Uncertain — not recommended without visual regression pass |
| P3 | **Critical CSS** for `/` only | L | FCP win; high maintenance |

## Non-goals (for now)

- Splitting Tailwind per route without a dedicated admin layout entry — cost &gt; benefit while gzip stays ~17 KB.
- Inlining OG/meta via CSS changes — use server `/og/news/{slug}` and static `index.html` tags instead.

See also: [Frontend guide](/guide/frontend), [P3 roadmap](/specs/p3-roadmap).
