---
name: ui-ux-pro-max
description: UI/UX overview, recommendations, and best practices for client UI
---

# UI/UX Pro Max

## When to apply

Use for new pages, UI refactors, interaction patterns, visual review, or UX quality control on the Vue client.

Skip for pure backend, API/database design, infra/DevOps, or non-visual scripts unless the change affects how something looks, feels, moves, or is interacted with.

## Precedence

| Layer | Owns |
|-------|------|
| `toss-style-design-system` | Visual language: spacing, typography, grayscale, accents, cards, dark mode |
| This skill | UX quality: a11y, touch, motion, forms, nav, UI performance, design recommendations |
| `.cursor/references/accessibility-checklist.md` | WCAG AA checklist before shipping UI |

If Toss and Pro Max conflict on look (decorative gradients, multi-accent, novelty), **Toss wins**. Pro Max still applies for interaction, a11y, and process.

## Priority overview (best practice)

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
- **Portfolio exception:** Toss already allows limited accent gradients on brand moments; product/admin stays single-accent.
- Before delivery: run `.cursor/references/accessibility-checklist.md`.

## Recommendation workflow

For non-trivial UI design or review, also read the user-level skill at `~/.agents/skills/ui-ux-pro-max/SKILL.md` and run its search script (do **not** copy that database into this repo):

```bash
python3 "$HOME/.agents/skills/ui-ux-pro-max/scripts/search.py" "<query>" --stack vue
# New pages / redesigns:
python3 "$HOME/.agents/skills/ui-ux-pro-max/scripts/search.py" "<product keywords>" --design-system -p "gLOrng" --stack vue
```

If the script is missing, install the ecosystem skill (`npx skills add …`) or fall back to the priority overview above and the a11y checklist—say when recommendations came from defaults, not a database match.

## Do / Don’t

**Do**

- Use semantic HTML and visible labels before ARIA.
- Keep focus rings; trap focus in modals; return focus on close.
- Reuse Toss spacing/type tokens and shared UI components.
- Provide loading and error states for async UI.

**Don’t**

- Use emoji as icons or remove outline without a `:focus-visible` replacement.
- Rely on hover-only affordances or color-only status.
- Invent one-off spacing/hex that bypasses tokens.
- Override Toss with decorative multi-accent product UI “because Pro Max suggested it.”
