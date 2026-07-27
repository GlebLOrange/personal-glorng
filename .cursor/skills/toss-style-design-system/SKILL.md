---
name: toss-style-design-system
description: Toss-style UI design rules for disciplined spacing, typography, grayscale hierarchy, restrained color, cards, metrics, dark mode, and accessibility
---

# Toss-Style Design System Rules

## Design Direction

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

## Layout and Rhythm

- Use consistent spacing tokens.
- Keep related content close and unrelated content separated by whitespace.
- Use section rhythm: summary, details, action, and supporting context.
- Align form fields, values, and controls predictably.
- Avoid nested cards and excessive borders.

## Cards and Surfaces

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

## Dark Mode

- Rebuild the grayscale scale for dark mode rather than inverting colors.
- Reduce bright accent intensity on dark backgrounds (pale tokens already do this).
- Preserve contrast between surface, border, and foreground layers.
- Test charts, cards, and form controls in both modes.
- Light defaults: page `#e5e7eb`, text `#111827`. Dark defaults: page `#111827`, text `#F9F9FB`.

## Accessibility

- Meet WCAG AA contrast for text and controls.
- Provide visible focus states.
- Keep tap targets large enough for touch.
- Use semantic HTML and labels before adding ARIA.
- Respect reduced motion preferences.

## Common Mistakes

- Do not create one-off spacing values.
- Do not mix multiple unrelated accent colors.
- Do not overuse cards to separate every piece of content.
- Do not rely on large hero typography inside dense product screens.
