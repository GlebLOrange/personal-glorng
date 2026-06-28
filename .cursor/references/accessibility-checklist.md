# Accessibility Checklist (WCAG 2.1 AA)

Use when building or reviewing UI. Pair this checklist with the Vue and design-system rules.

## Perceivable

### Text and Contrast

- [ ] Normal text meets 4.5:1 contrast ratio against its background
- [ ] Large text (18px+ regular or 14px+ bold) meets 3:1 contrast ratio
- [ ] UI components and graphical objects meet 3:1 contrast against adjacent colors
- [ ] Text remains readable when zoomed to 200% (no horizontal scroll for body content)
- [ ] Color is not the sole means of conveying information (add icons, text, or patterns)

**Red flags:** Light gray on white body text, status indicators that are only red/green, disabled states invisible to low-vision users.

### Images and Media

- [ ] Informative images have descriptive `alt` text
- [ ] Decorative images use `alt=""` or `aria-hidden="true"`
- [ ] Complex images (charts, diagrams) have a text alternative or longer description
- [ ] Video/audio has captions or transcripts where applicable

**Red flags:** Missing `alt` on icons that convey meaning, `alt="image"`, auto-playing media without controls.

### Structure

- [ ] Page has a unique, descriptive `<title>`
- [ ] Heading hierarchy is logical (h1 → h2 → h3, no skipped levels)
- [ ] Landmarks used appropriately (`main`, `nav`, `header`, `footer`)
- [ ] Lists use semantic `<ul>`, `<ol>`, `<li>` (not styled divs)

**Red flags:** Multiple h1 elements, heading styles on non-heading elements, div soup with no landmarks.

## Operable

### Keyboard Access

- [ ] All interactive elements reachable and operable via keyboard alone
- [ ] Tab order follows visual reading order
- [ ] No keyboard traps (user can Tab away from every focusable element)
- [ ] Custom widgets implement expected keys (Enter/Space for buttons, arrows for menus)
- [ ] Skip link present to bypass repeated navigation blocks

**Red flags:** Clickable `<div>` without `tabindex` and key handlers, `outline: none` without a visible focus alternative.

### Focus

- [ ] Focus indicator is visible on all interactive elements (`:focus-visible` ring or equivalent)
- [ ] Focus moves to newly opened dialogs/modals on open
- [ ] Focus returns to trigger element when dialogs close
- [ ] Focus is trapped inside modal dialogs while open

**Red flags:** Invisible focus rings, background scroll while modal is open, focus lost after closing a dialog.

### Touch and Motion

- [ ] Touch targets are at least 44×44 CSS pixels (or have sufficient spacing)
- [ ] No content flashes more than 3 times per second
- [ ] `prefers-reduced-motion` respected for animations and transitions

**Red flags:** Tiny icon-only buttons with no padding, parallax or auto-animations with no reduced-motion fallback.

## Understandable

### Labels and Instructions

- [ ] Every form input has a visible `<label>` or `aria-label` / `aria-labelledby`
- [ ] Required fields are indicated (not by color alone)
- [ ] Error messages identify the field and describe how to fix the problem
- [ ] Error messages are associated with inputs via `aria-describedby` or `aria-invalid`

**Red flags:** Placeholder text used as the only label, generic "Invalid input" errors, errors shown only in color.

### Consistency and Language

- [ ] Navigation and component patterns are consistent across pages
- [ ] Page language set via `<html lang="...">`
- [ ] Language changes within content marked with `lang` attribute
- [ ] Unexpected context changes (auto-submit, auto-navigate) do not occur on focus alone

**Red flags:** Different button styles for the same action type, form submitting on blur, missing `lang` on mixed-language content.

## Robust

### Semantic HTML

- [ ] Native HTML elements used where possible (`button`, `a`, `input`, `select`, `textarea`)
- [ ] Links used for navigation; buttons used for actions
- [ ] Tables used for tabular data with `<th scope="...">` headers
- [ ] ARIA roles used only when native semantics are insufficient

**Red flags:** `<a @click.prevent>` for non-navigation actions, `<button>` wrapping links, redundant ARIA (`role="button"` on `<button>`).

### ARIA

- [ ] ARIA attributes match element behavior (expanded, selected, checked, disabled)
- [ ] Live regions (`role="status"`, `aria-live`) used for dynamic content updates
- [ ] `aria-hidden="true"` not applied to focusable elements
- [ ] Icon-only buttons have `aria-label`

**Red flags:** Static `aria-expanded="false"` that never updates, hiding focusable content with `aria-hidden`, duplicate labels.

### Vue-Specific

- [ ] `v-html` used only with sanitized content (e.g. DOMPurify)
- [ ] Dynamic `:id` bindings connect labels to inputs correctly
- [ ] Teleported modals (e.g. `<Teleport to="body">`) retain focus management
- [ ] Conditional rendering (`v-if`) does not leave orphaned focus on removed elements
- [ ] `@keydown` handlers on custom widgets mirror native behavior

**Red flags:** Raw `v-html` on user content, label `for` pointing to a non-existent id after re-render, focus stuck on unmounted element.

## Testing Tools

Run at least one automated and one manual pass before considering UI complete:

| Tool | What it checks |
|------|----------------|
| **axe DevTools** (browser extension) | WCAG violations in the DOM |
| **Lighthouse** (Chrome DevTools → Accessibility) | Automated audit score and issues |
| **Keyboard-only pass** | Tab through entire flow; verify all actions work without a mouse |
| **VoiceOver** (macOS/iOS) or **NVDA** (Windows) | Screen reader announces structure, labels, and state changes |
| **Browser zoom 200%** | Layout and readability at increased zoom |
| **Color contrast checker** | Verify token pairs meet ratio requirements |

## Severity Guide

| Finding | Severity |
|---------|----------|
| Keyboard-inaccessible primary action, missing form labels | **Critical** — blocks merge |
| Missing alt on informative images, no focus indicator | Required — must fix |
| Heading level skip, insufficient touch target size | Required — must fix |
| Missing skip link on content-heavy layout | **Optional** — suggest |
| Redundant ARIA on native element | **Nit** — clean up when touching the file |
