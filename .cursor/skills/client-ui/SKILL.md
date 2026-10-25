---
name: client-ui
description: >-
  Toss-style visual language plus UX and accessibility priorities for the Vue client.
  Use when changing pages, layout, styling, motion, forms, or accessibility.
---

# Client UI

## When to apply

Use for new pages, UI refactors, interaction patterns, visual review, or UX quality control on the Vue client.

Skip for pure backend, API/database design, infra/DevOps, or non-visual scripts unless the change affects how something looks, feels, moves, or is interacted with.

## Precedence

| Layer | Owns |
|-------|------|
| Visual language (below) | Spacing, typography, grayscale, accents, cards, dark mode — **wins on look** |
| UX priorities (below) | A11y, touch, motion, forms, nav, UI performance, recommendations |
| `.cursor/references/accessibility-checklist.md` | WCAG AA checklist before shipping UI |

If visual language and UX priorities conflict on look (decorative gradients, multi-accent, novelty), **visual language wins**. UX priorities still apply for interaction, a11y, and process.

## Design direction

- Build quiet, high-trust product UI with clear hierarchy, generous spacing, and minimal ornament.
- Use one primary accent color and rely on grayscale for most structure.
- Avoid decorative gradients, unnecessary shadows, and competing accent colors.
- Prioritize readability, confidence, and fast scanning over visual novelty.

## Typography

- Use a strict type scale with clear roles for page title, section title, body, supporting text, and metadata.
- Use font weight and color before using large size changes.
- Never use pure black text; use a dark grayscale foreground.
- Keep line height comfortable for body copy and tighter for short labels or metrics.
- For metrics, make the number visually dominant and the unit smaller but still legible.

## Layout and rhythm

- Use consistent spacing tokens.
- Keep related content close and unrelated content separated by whitespace.
- Use section rhythm: summary, details, action, and supporting context.
- Align form fields, values, and controls predictably.
- Avoid nested cards and excessive borders.

## Cards and surfaces

- Use cards only for grouped content that needs a surface.
- Keep card radius restrained and consistent.
- Use subtle shadows or borders, not both heavily.
- Keep shadow opacity low and avoid dramatic elevation.
- Do not place important controls in low-contrast decorative surfaces.
- Interactive cards, tiles, and action pills: **idle = `border-transparent`** (surface/fill separates units). **Hover / selected / active** = accent (or family) border; **focus-visible** = ring (not a permanent border).
- Do not add idle `border-surface-border` on hoverable tiles to “fix” separation — use spacing, type, and surface contrast instead.
- Exception: structural chrome (nav/page chrome dividers, form fields, tables) may keep always-on borders. Selected weather (`border-accent-blue` on the weather page) counts as selected and is allowed.

## Color

- Use the accent color for primary actions, selected state, links, or critical brand moments.
- Use semantic colors for status only: success, warning, error, and information.
- Keep disabled and secondary states in grayscale.
- Ensure status is never communicated by color alone.
- Prefer **pale** (desaturated) status/brand tokens — not saturated neon fills. Solid CTAs use pale `accent-blue` with `on-accent` ink.
- Dual theme: rebuild grayscale per mode via `html[data-theme]`; preference is **dark** or **light** (default dark). Same token names in light and dark.

## Marketing / portfolio exception

Portfolio and marketing surfaces may use `accent-blue`, `accent-violet`, `accent-golden`, and `.accent-gradient` on brand name moments. Product and admin UI stays on a single `accent-blue` accent — no decorative gradients on buttons or tool screens.

## Dark mode

- Rebuild the grayscale scale for dark mode rather than inverting colors.
- Reduce bright accent intensity on dark backgrounds (pale tokens already do this).
- Preserve contrast between surface, border, and foreground layers.
- Test charts, cards, and form controls in both modes.
- Light defaults: page `#e5e7eb`, text `#111827`. Dark defaults: page `#111827`, text `#F9F9FB`.

## Accessibility (visual)

- Meet WCAG AA contrast for text and controls.
- Provide visible focus states.
- Keep tap targets large enough for touch.
- Use semantic HTML and labels before adding ARIA.
- Respect reduced motion preferences.

## UX priority overview

Follow 1→10; fix higher priorities before polishing lower ones.

1. **Accessibility** — Contrast 4.5:1, alt text, keyboard nav, aria-labels; never remove focus rings or ship icon-only buttons without labels.
2. **Touch & interaction** — Min 44×44px targets, 8px+ spacing, loading feedback; no hover-only actions or 0ms state flips.
3. **UI performance** — WebP/AVIF, lazy load, reserve space (CLS); avoid layout thrashing.
4. **Style consistency** — Match product type; SVG icons (no emoji as icons); do not mix flat and skeuomorphic randomly.
5. **Layout & responsive** — Mobile-first, viewport meta, no horizontal scroll; no fixed-px container traps or disabled zoom.
6. **Typography & color** — Base 16px, line-height ~1.5, semantic tokens; no raw hex in components, no gray-on-gray body.
7. **Animation** — 150–300ms, motion with meaning; respect `prefers-reduced-motion`; do not animate width/height for decoration.
8. **Forms & feedback** — Visible labels, errors near fields, helper text; no placeholder-only labels.
9. **Navigation** — Predictable back, focused nav, deep links; avoid overloaded menus and broken history.
10. **Charts & data** — Legends, tooltips, accessible colors; never color alone for meaning.

## Repo defaults

- **Product:** developer portfolio + admin SaaS hybrid.
- **Stack:** Vue 3 + Vite + Tailwind; prefer `client/src/components/ui/` primitives and existing design tokens.
- Before delivery: run `.cursor/references/accessibility-checklist.md`.

## Recommendation workflow

For non-trivial UI design or review, also read the user-level skill at `~/.agents/skills/ui-ux-pro-max/SKILL.md` and run its search script (do **not** copy that database into this repo):

```bash
python3 "$HOME/.agents/skills/ui-ux-pro-max/scripts/search.py" "<query>" --stack vue
# New pages / redesigns:
python3 "$HOME/.agents/skills/ui-ux-pro-max/scripts/search.py" "<product keywords>" --design-system -p "Gleb.Y" --stack vue
```

If the script is missing, install the ecosystem skill (`npx skills add …`) or fall back to the priority overview above and the a11y checklist—say when recommendations came from defaults, not a database match.

## Do / don’t

**Do**

- Use semantic HTML and visible labels before ARIA.
- Keep focus rings; trap focus in modals; return focus on close.
- Reuse spacing/type tokens and shared UI components.
- Provide loading and error states for async UI.

**Don’t**

- Use emoji as icons or remove outline without a `:focus-visible` replacement.
- Rely on hover-only affordances or color-only status.
- Invent one-off spacing/hex that bypasses tokens.
- Override the visual language with decorative multi-accent product UI “because a UX search suggested it.”
- Create one-off spacing values or overuse cards to separate every piece of content.
- Rely on large hero typography inside dense product screens.
