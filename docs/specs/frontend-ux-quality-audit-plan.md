# Frontend UX / Quality Audit Plan (Draft)

**Status:** draft — review only, no implementation in this change  
**Scope:** `client/` SPA only (Vue 3 + Vite + Tailwind). AMP is noted where the client links to it; server AMP HTML is out of scope except for client `<link rel="amphtml">` contract.  
**Standards:** Toss design system (visual), UI/UX Pro Max (interaction / a11y / process), `.cursor/references/accessibility-checklist.md`, `.cursor/references/performance-checklist.md`, DevSecOps frontend hygiene.  
**Recommendation source:** repo skills + checklists. Ecosystem `ui-ux-pro-max` search DB was not available in this environment; fall back to priority overview in the skill.

---

## 0. How to read this plan

For every issue:

1. **Finding** — what is wrong (file refs)  
2. **Why bad** — user / SEO / security / maintainability impact  
3. **Solution** — minimal fix  
4. **Why better** — outcome  
5. **Self-check** — quick verification that the first pass was not a false positive  

Severity: **P0** ship-blocker / security · **P1** a11y or UX correctness · **P2** DRY / maintainability · **P3** polish / nice-to-have.

---

## 1. Cross-cutting strengths (keep)

| Area | What works |
|------|------------|
| Route splitting | Every route uses `() => import(...)` in `router/index.ts` |
| Below-fold deferral | Portfolio async sections + IntersectionObserver for donations; Expenses charts via `defineAsyncComponent` |
| Auth model | Cookie session + `withCredentials`; no JWT in `localStorage` |
| Redirect / URL hygiene | `safeRedirectPath`, `scrubSensitivePath`, `consumeQueryParams` + tests |
| XSS posture | Almost no `v-html`; Email preview uses DOMPurify |
| Image URL gate | `safeImageSrc` blocks `javascript:`, `data:`, `blob:`, protocol-relative |
| Shell a11y | Skip link → `#main-content`, NavBar landmark, focus styles in `main.css`, `prefers-reduced-motion` |
| List chrome | Shared admin toolbar / filters / footer / EmptyState / ErrorState on most tools |
| SEO runtime | `applyRouteSeo` / `applyPageSeo` with auth ⇒ `noindex` |

---

## 2. Cross-cutting issues (fix all pages)

### 2.1 Accessible names vs placeholder tips — **P1**

**Finding:** `BaseInput` intentionally never uses `placeholder` as the accessible name (tip is `aria-hidden`). Many pages pass only `placeholder=...` without `label` or `aria-label` (Settings often uses `aria-label`; NewsArticleAdmin, UrlShortener, VidDownload, AdminSearch, AppLogs, Email, AiChat textarea, etc. do not).

**Why bad:** Screen readers announce an unnamed textbox; fails WCAG 1.3.1 / 4.1.2; Pro Max forms rule (“no placeholder-only labels”).

**Solution:** Audit every `BaseInput` / `BaseTextarea` / native control: require `label` (preferred) or `aria-label`. Add a lint rule or unit assertion on critical forms. Prefer visible labels in dense admin forms.

**Why better:** Predictable names; fewer support bugs; matches `BaseInput` contract.

**Self-check:** Grep `placeholder=` without nearby `label=` / `aria-label=`; axe or vitest mount asserts `getByRole('textbox', { name: ... })` on Login, AdminSearch, NewsArticleAdmin, UrlShortener, VidDownload, AiChat.

---

### 2.2 Image pipeline vs CSP — **P0/P1**

**Finding:** `safeImageSrc` allows any `https:` URL. Prod nginx CSP `img-src` is a narrow allowlist. `BaseImage` always loads `/images/placeholder.svg` eagerly **plus** the lazy real image (double decode). No `srcset` / WebP / AVIF strategy. Only `public/images/placeholder.svg` + favicons in `public/`.

**Why bad:** Recipe/remote images can pass client validation then break in prod; CLS/bandwidth waste from dual `<img>`; no responsive density; CSP pressure to widen allowlist (security regress).

**Solution:** Align allowlist (or proxy images via same-origin `/media`); change `BaseImage` to CSS/skeleton placeholder (no eager img) until real load; add optional `srcset` for known assets; keep SVG icons as Vue SFCs (current pattern is fine).

**Why better:** Images that work under CSP; less work on LCP path; safer media policy.

**Self-check:** Confirm nginx `img-src` list vs `safeImageSrc` policy in a unit test matrix; Lighthouse on Recipes + Portfolio; network panel shows one image request per `BaseImage` after fix.

---

### 2.3 Auth shell + password field DRY — **P2**

**Finding:** Login / Register / Forgot / Reset / Verify / Callback repeat layout shells; password strength + confirm mismatch UI duplicated across Register, Reset, Settings.

**Why bad:** Drift (Login already uses a different vertical centering); policy UI can diverge from `passwordPolicy.ts`.

**Solution:** One `AuthPageShell` + one `PasswordFields` (strength meter, confirm, `aria-describedby`). Keep page-specific copy/actions only.

**Why better:** One place to fix a11y/focus after errors; policy messaging stays consistent.

**Self-check:** Diff the six auth pages after extract — only form fields/actions remain unique; password policy tests cover the shared component.

---

### 2.4 DOMPurify hook lifecycle (Email) — **P1**

**Finding:** `sanitizeEmailHtml` add/remove hooks per call → race if concurrent.

**Why bad:** Rare XSS/window for `rel` injection failure under concurrent preview/send.

**Solution:** Register hooks once at module load (or use DOMPurify config without mutable global hooks).

**Why better:** Deterministic sanitization under concurrency.

**Self-check:** Existing `sanitizeEmailHtml.test.ts` still green; add concurrent `Promise.all` sanitize test.

---

### 2.5 Nested `<main>` landmark — **P1**

**Finding:** `App.vue` wraps all routes in `<main id="main-content">`. `RecipeCookMode.vue` nests another `<main>`.

**Why bad:** Invalid landmark tree; AT users get ambiguous “main” regions.

**Solution:** Change cook mode inner wrapper to `<div role="region" aria-label="Cook mode">` (or dialog pattern if fullscreen).

**Why better:** One main landmark per page.

**Self-check:** axe / HTML outline — only one `main` while cook mode open.

---

### 2.6 Admin list row keyboard gap — **P1**

**Finding:** `AdminListRow` with `nestedInteractive` disables row focus/activation (Feedback, NewsSources). Nested icon buttons work; whole-row open is mouse-only.

**Why bad:** Unequal keyboard UX; easy to miss for power users.

**Solution:** Keep nested buttons; add explicit “Open” control or make the title a focusable button/link; do not nest interactive in interactive.

**Why better:** Full keyboard parity without invalid HTML nesting.

**Self-check:** Tab-only open/edit/delete on Feedback + NewsSources rows.

---

### 2.7 Bundle / vendor chunking — **P2**

**Finding:** `vite.config.ts` `manualChunks` only for charts / firebase / vue-vendor. Axios, DOMPurify, cookieconsent, fonts stay in default graph. Full IBM Plex weights always imported.

**Why bad:** Larger initial JS/CSS than needed for public marketing paths.

**Solution:** Chunk `axios`, `dompurify`, cookie consent; subset/lazy fonts where possible; keep charts async (already good). Optionally analyze with `ANALYZE=true`.

**Why better:** Faster TTI on Portfolio / News / public tools.

**Self-check:** Compare `dist/stats.html` before/after; Portfolio route does not pull charts/firebase.

---

### 2.8 Static OG image URLs — **P2**

**Finding:** `index.html` uses relative `og:image` / `twitter:image`. Runtime SEO absolutizes after JS; non-JS / early crawlers may miss absolute image.

**Why bad:** Weaker social previews for cold crawls.

**Solution:** Absolute OG URLs in `index.html` (or SSR/prerender for key public routes). Keep runtime `pageSeo` for per-page updates.

**Why better:** Predictable share cards without waiting for hydration.

**Self-check:** `curl -s` homepage HTML shows absolute `og:image`; Facebook/Twitter debugger (manual) OK.

---

### 2.9 AMP coverage misconception — **P2** (client contract)

**Finding:** Client always emits `<link rel="amphtml" href="/amp" />` on **every** SPA shell load. Server only serves portfolio AMP at `/amp`. No article AMP.

**Why bad:** News/tools pages advertise an AMP alternate that is the portfolio, not the current URL — misleading for crawlers and AMP caches.

**Solution (client-facing):** Emit `amphtml` only on portfolio route (runtime `useRouteSeo` / conditional head), or remove static tag from `index.html` and set it when `route.name === 'portfolio'`. Longer-term (out of this SPA plan): per-article AMP or drop AMP claim for non-portfolio.

**Why better:** AMP alternate matches the page being viewed.

**Self-check:** View-source / head manager on `/`, `/news`, `/news/:slug` — amphtml only where intended.

---

### 2.10 Inconsistent async/error primitives — **P2**

**Finding:** Many tools use `useApiAction` + shared ErrorState; Audit / AppLogs / AdminSearch / NewsSources hand-roll loading/error differently.

**Why bad:** Inconsistent retry UX; more copy-paste bugs.

**Solution:** Standardize on `useApiAction` (or thin list composable) + ErrorState/EmptyState/ListSkeleton.

**Why better:** One loading/error pattern across admin.

**Self-check:** Spot-check error retry on Audit, AppLogs, Search, NewsSources matches Feedback.

---

### 2.11 Focus management on auth errors — **P1**

**Finding:** Auth forms show `role="alert"` but do not move focus to the alert or first invalid field after submit failure.

**Why bad:** SR users may not notice the error; keyboard users stay on Submit.

**Solution:** On failure, `focus()` the alert or first invalid input (`focusField` util already exists).

**Why better:** Operable error recovery (WCAG 3.3.1 / 3.3.3).

**Self-check:** Failed login → focus lands on error or email field; Register validation same.

---

### 2.12 Test gaps on security-critical client paths — **P1**

**Finding:** Strong tests for `safeUrl`, `safeImageSrc`, `sensitiveUrl`, `sanitizeEmailHtml`, scroll restore. Missing/weak: `passwordPolicy.test.ts`, `useApi` 401 refresh queue, most auth pages beyond Login, `streamingPost` retry.

**Why bad:** Regressions in auth/session refresh or password rules slip to prod.

**Solution:** Add focused unit tests; keep UI tests thin.

**Why better:** Safety net matching the already-good URL helpers.

**Self-check:** CI covers refresh-queue + password policy edge cases.

---

## 3. Page-by-page review

Legend for page status after current strengths: **OK** (minor only) · **Needs work** · **Priority fix**.

---

### 3.1 Portfolio — `/` (`PortfolioPage.vue`) — **OK**

**Strengths:** Async below-fold chunks; donations deferred via IntersectionObserver; ErrorState/EmptyState; skip-link friendly; brand-forward hero composition via `HeroBlock` (fits portfolio Toss exception for accents).

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P3 | Spotify embed / third-party may affect CLS/privacy | Extra layout shift / cookies | Keep lazy mount; ensure reserved aspect box; consent-gated if analytics-tied | Cleaner LCP / consent story | Network idle until section near viewport |
| 2 | P2 | Global amphtml points at portfolio AMP even when user later navigates client-side | Stale head if not updated | Tie amphtml to portfolio route only (see 2.9) | Correct AMP discovery | Head on `/` has amphtml; after client nav to `/news` it is removed |

**Best-practices pass:** Semantics (sections), lazy loading, motion respect via shared scroll helpers — **pass with AMP head caveat**.

---

### 3.2 Login — `/login` (`LoginPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | No focus move to `role="alert"` on error | Errors easy to miss for AT | Focus alert / email via `focusField` | Clear failure feedback | Fail login with keyboard only |
| 2 | P2 | Layout differs from other auth pages | Visual/UX drift | Shared `AuthPageShell` | Consistent entry UX | Side-by-side Register/Login |
| 3 | P3 | Google “G” text as brand mark | Weak icon semantics | SVG Google mark with `aria-hidden` + labeled button | Clearer branding, no emoji/text hack | Button name still “Continue with Google” |

**Security note:** `safeRedirectPath` — **keep**.  
**Best-practices pass:** Labels present — **pass** after focus fix.

---

### 3.3 Register — `/register` (`RegisterPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Password strength UI duplicated | Drift vs Reset/Settings | Shared `PasswordFields` | One policy UX | Strength messages identical |
| 2 | P1 | Error focus same as Login | AT miss | Focus first invalid / alert | Operable forms | Submit empty → focus |

**Best-practices pass:** Terms checkbox labeled, strength `aria-describedby` — **mostly pass**.

---

### 3.4 Verify email — `/verify-email` (`VerifyEmailPage.vue`) — **OK**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P3 | No page-level test | Token consume regressions | Small test: token scrubbed + states | Safer auth funnel | `consumeQueryParams` asserted |

**Best-practices pass:** Live regions, token scrub — **pass**.

---

### 3.5 Forgot password — `/forgot-password` (`ForgotPasswordPage.vue`) — **OK**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Shell duplication | Drift | Auth shell | Consistency | Matches Login chrome |
| 2 | P1 | Confirm email field has accessible name? (placeholder pattern) | Unnamed field risk | Ensure `label`/`aria-label` | Named control | `getByLabelText` |

**Best-practices pass:** Anti-enumeration copy — **pass** if name fixed.

---

### 3.6 Reset password — `/reset-password` (`ResetPasswordPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Password UI duplication | Drift | Shared fields | Single policy UI | Matches Register |
| 2 | P1 | Focus on missing-token / validation | Missed errors | Focus alert | Operable recovery | Open without token |

**Security:** Token consume + scrub — **keep**.  
**Best-practices pass:** After shared fields + focus — **pass**.

---

### 3.7 Settings — `/settings` (`SettingsPage.vue`, ~437 lines) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | XL monolith (profile, email, password, currency, GitHub, delete) | Hard to review / test | Split section components | Smaller blast radius | Each section ≤150 lines |
| 2 | P1 | `aria-label` instead of visible labels | Weaker for sighted + zoom users | Visible `<label>` via BaseInput `label` | Matches forms checklist | Visual labels on all fields |
| 3 | P2 | Password strength duplicated again | Drift | Shared PasswordFields | Consistency | Same meter as Register |
| 4 | P3 | Hard nav to GitHub authorize | Full reload OK for OAuth; document | Keep; ensure return path scrubbed | Secure OAuth | Callback still works |

**Best-practices pass:** Auth-gated, noindex — **pass structure**; labels need upgrade.

---

### 3.8 Tools catalog — `/tools` (`ToolsPage.vue`) — **OK**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P3 | No empty state if catalog empty | Blank page edge | EmptyState | Clear recovery | Mock empty catalog |
| 2 | P2 | Tile grid mirrors Admin dashboard | DRY drift | Shared `ToolTileGrid` | One tile UX | Same a11y on both |

**Best-practices pass:** Card-as-link interaction — **pass**.

---

### 3.9 News route switch — `/news` (`NewsRoutePage.vue`) — **OK**

Async switch public vs admin manage mode — good pattern.  
**Self-check:** Guest never loads NewsAdmin chunk; `?manage=1` without permission stays public.

---

### 3.10 News digest — `NewsPage.vue` — **OK**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P3 | Card overlay links — ensure hit target ≥44px | Touch miss | Padding / min-height on row | Touch-friendly | Mobile tap test |
| 2 | P2 | Source links use `safeNavigationHref` (good) — keep pattern elsewhere | — | Document as standard | Consistent security | AdminSearch should match |

**Best-practices pass:** Loading/error/empty, safe external links — **pass**.

---

### 3.11 News article — `/news/:slug` (`NewsArticlePage.vue`) — **Priority fix**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P0/P1 | **No `<h1>` / article title in body** — chrome title prefers URL slug; body starts with summary `<p>` | Broken outline, weak SEO, confusing readers | Render `article.title` as `<h1>`; breadcrumbs can keep truncated slug | Correct document outline + share of meaning | DOM has one h1 = title |
| 2 | P2 | Themes as spans only | Themes not a list semantically | `<ul>` of theme tags | Better structure | List role present |
| 3 | P3 | No article AMP alternate | amphtml still portfolio | Don’t claim article AMP (2.9) | Honest discovery | No false amphtml on article |

**Security:** Text nodes + safe source URL — **good**.  
**Best-practices pass:** **Fail** until h1/title fixed; then re-pass.

---

### 3.12 Weather — `/weather` (`WeatherPage.vue` + weather components) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Weather conditions use emoji (`aria-hidden`) + text | Emoji as visual icon (Pro Max: avoid emoji as icons) | SVG weather glyphs or keep text-only | Consistent icon system | No emoji-as-sole-icon |
| 2 | P3 | Guest locations in localStorage | Fine if sanitized (is) | Keep `sanitizeGuestWeatherLocations` | Safe guest prefs | Tampered JSON ignored |
| 3 | P3 | Live time updates — ensure reduced-motion / battery OK | Timer noise | Pause when tab hidden | Cheaper idle | `document.hidden` stops ticks |

**Best-practices pass:** Landmarks on WeatherBar, labeled city actions — **mostly pass**.

---

### 3.13 Privacy — `/privacy` (`PrivacyPage.vue`) — **OK**

Good h1→h2, cookie table, consent button.  
**Self-check:** Feature-flagged analytics rows match actual consent categories.

---

### 3.14 Not found — `*` (`NotFoundPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Minimal 404 — only BackLink | Dead-end UX | Link to `/`, `/tools`, `/news`; unique title already | Recoverable navigation | Three recovery links |
| 2 | P3 | No `h1` emphasis beyond chrome | Weak semantics | Explicit “Page not found” h1 via PageShell | Clear status | Outline OK |

**Best-practices pass:** After recovery links — **pass**.

---

### 3.15 OAuth callback — `/callback` (`CallbackPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Route meta missing explicit `title` | Relies on requiresAuth side effects | Add `title` + `noindex` | Clear SEO/meta | Document title set |
| 2 | P3 | Unicode ✓/✗ decorative | Fine with aria-hidden | Prefer SVG status icons | Icon system consistency | Status text still spoken |
| 3 | P3 | Auto-redirect 2s | Can surprise | Announce countdown / link “Continue now” | User control | Can navigate immediately |

**Best-practices pass:** Live region + code/state consume — **pass** with meta polish.

---

### 3.16 Admin dashboard — `/admin` (`DashboardPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | No loading skeleton while catalog loads | Empty flash | ListSkeleton / pulse tiles | Stable first paint | Slow 3G: no blank gap |
| 2 | P2 | Tile grid duplicated with ToolsPage | Drift | Shared grid | DRY | Same external-link a11y |

**Best-practices pass:** External docs `rel` + aria — **pass** after loading state.

---

### 3.17 Admin users — `/admin/users` (`AdminUsersPage.vue`, ~460) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | XL page | Hard review | Extract filters + grid + permissions drawer container | Maintainable | Page becomes composition |
| 2 | P3 | Search input labeling | Risk of unnamed search | Use `SearchInput` / labeled field | Named search | AT announces “Search users” |

**Best-practices pass:** Cards as buttons, discard confirm — **pass** structure.

---

### 3.18 Feedback — `/admin/feedback` (`FeedbackPage.vue`) — **Priority fix**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | Opening item **auto-archives** | Surprising destructive side effect | Explicit “Archive” action; open = read only | Predictable admin UX | Open item ≠ status change |
| 2 | P1 | Reply puts body into `query.body` for EmailTool | History leakage, URL length, sensitive content in logs/referrers | Use sessionStorage / shared store / POST draft id | No secrets in URL | History has no message body |
| 3 | P1 | `nestedInteractive` rows not keyboard-openable | Mouse-only open | Title button / Open control | Keyboard parity | Tab+Enter opens drawer |

**Best-practices pass:** **Fail** until archive + URL body fixed.

---

### 3.19 Audit logs — `/admin/audit-logs` (`AuditPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Hand-rolled loading/error | Inconsistent | `useApiAction` + ErrorState | Shared UX | Matches Feedback |
| 2 | P2 | Expandable rows — ensure keyboard | Operable disclosure | `button` + `aria-expanded` | A11y disclosure | Arrow/Enter toggles |

**Best-practices pass:** After keyboard disclosure — **pass**.

---

### 3.20 App logs — `/admin/app-logs` (`AppLogsPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | Request-id input placeholder-only | Unnamed field | `label` / `aria-label` | Named filter | AT name present |
| 2 | P2 | Same expandable + error pattern drift as Audit | Inconsistency | Shared log list primitive | DRY | One component for both |

**Best-practices pass:** After naming + disclosure — **pass**.

---

### 3.21 Admin search — `/admin/search` (`AdminSearchPage.vue`) — **Priority fix**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P0 | `RouterLink :to="hit.url"` unsanitized | Open-redirect / unexpected navigation if API returns absolute/`//` URL | Resolve with same-origin path helper (mirror `safeRedirectPath` / allowlist relative paths only); reject externals | Matches News `safeNavigationHref` discipline | Evil `//evil` hit does not navigate out |
| 2 | P1 | Search field unlabeled | Unnamed textbox | `aria-label="Search admin content"` or `label` | Forms a11y | `getByRole('textbox', { name: /search/i })` |
| 3 | P2 | Hand-rolled fetch | Drift | `useApiAction` | Consistent errors | Retry works |

**Best-practices pass:** **Fail** until URL sanitization + label.

---

### 3.22 AI chat — `/admin/ai-chat` (`AiChatTool.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | Message textarea placeholder-only | Unnamed | `aria-label="Message"` | Named composer | AT name |
| 2 | P2 | Inline SVG refresh vs shared icons | Icon drift | Shared icon component | DRY | One refresh icon |
| 3 | P3 | Streaming UI — ensure live region for new tokens (careful: noise) | AT may miss replies | `aria-live="polite"` on completed message, not every token | Usable chat for AT | New message announced once |

**Security:** Feature flag + superuser — **keep**.  
**Best-practices pass:** After composer name — **pass**.

---

### 3.23 Email tool — `/admin/send-email` (`EmailTool.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | DOMPurify hook race (2.4) | Concurrent sanitize risk | One-time hooks | Stable sanitize | Concurrent test |
| 2 | P1 | Query prefill for body (from Feedback) | Sensitive URL history | Non-URL draft channel | No body in history | URL clean |
| 3 | P2 | Preview not a live region | SR may miss preview update | `aria-live="polite"` on preview pane | Preview announced | Preview update spoken |
| 4 | P1 | Fields use aria-label — OK if present; verify all three | — | Keep labels | Named fields | Names: to/subject/body |

**Best-practices pass:** v-html gated — **pass** after hook + draft channel.

---

### 3.24 Calculator — `/calculator` (`CalculatorTool.vue`) — **OK**

Strong a11y (live region, operator labels).  
**Self-check:** Reduced motion still usable; keypad targets ≥44px on mobile.

---

### 3.25 Expense calculator (public) — `/expense-calculator` (`ExpenseCalculatorTool.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Persistence hint duplicated with Expenses calculator tab | Copy drift | Shared helper/composable text | One source | Same hint both places |

**Best-practices pass:** Session resolve redirect for entitled users — **pass**.

---

### 3.26 Password generator — `/password-generator` (`PasswordGeneratorTool.vue`) — **OK**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P3 | Ensure copy control has accessible name | Icon button risk | IconCopyButton default label | Named action | Button name “copy” |
| 2 | P1 | Align generated charset with `passwordPolicy` messaging | User confusion | Reference same policy helpers | Consistent strength story | Policy tests cover generator options |

**Best-practices pass:** **pass** with copy name check.

---

### 3.27 Recipes — `/recipes` (`RecipesPage.vue` + drawers) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Single-tab `AdminTabBar` (“all” only) | Dead chrome / noise | Remove tab bar until multiple surfaces | Cleaner UI | No useless tabs |
| 2 | P2 | Reuses `ExpenseConfirmDialog` for delete | Domain leak / wrong copy risk | Generic `ConfirmDialog` | Reusable tool | Dialog title “Delete recipe” |
| 3 | P1 | Nested `<main>` in cook mode (2.5) | Bad landmarks | Region/dialog | Valid outline | One main |
| 4 | P1 | Images via BaseImage — CSP mismatch risk (2.2) | Broken images in prod | Align media policy | Reliable thumbnails | Recipe image loads under CSP |
| 5 | P2 | `RecipeFormDrawer` XL (~441) | Hard to maintain | Split fields groups | DRY forms | Drawer <250 lines |

**Best-practices pass:** List states good — **fail** cook-mode landmark + CSP images until fixed.

---

### 3.28 URL shortener — `/shortener` (`UrlShortenerTool.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | URL/title inputs placeholder-only | Unnamed | Labels | Forms a11y | Named fields |
| 2 | P3 | Public create vs manage list gating | OK if clear | Empty/disabled messaging when !canManage | Clear auth boundary | Guest sees create only |

**Best-practices pass:** After labels — **pass**.

---

### 3.29 Video download — `/vid-download` (`VidDownloadTool.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | URL input placeholder-only | Unnamed | Label | A11y | Named field |
| 2 | P3 | Options dialog — already labeled | — | Keep | Good pattern | Focus trap works |
| 3 | P3 | Blob revoke after download | Good | Keep | No blob leak | Revoke called |

**Best-practices pass:** Dialog a11y good — **pass** after URL label.

---

### 3.30 File share — `/file-share` (`FileShareTool.vue`) — **OK**

Drop zone labeled; skeleton/empty/pagination present.  
**Self-check:** Touch target on drop zone; error on upload failure visible near control.

---

### 3.31 Tasks — `/tasks` (`TasksPage.vue`, ~316) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | Large page with tabs | Hard to test | Extract tab panels | Smaller units | Page composes panels |
| 2 | P3 | Filter inputs naming | Risk | Labels on filters | A11y | Named filters |

**Best-practices pass:** Tabpanels `aria-labelledby` — **pass** structure.

---

### 3.32 Expenses — `/expenses` (`ExpensesTool.vue` + charts) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P2 | `useExpensesTool` ~642 lines | Logic bottleneck | Split list / insights / settings composables | Testable units | No god-composable |
| 2 | P2 | Insights imports all three Chart wrappers at once | Charts chunk always full | Lazy per-chart or single registry module | Smaller insights path | Network: only needed chart |
| 3 | P2 | Chart hex colors duplicate CSS tokens | Theme drift | Read CSS variables in `chartTheme` | Dark/light sync | Token change updates charts |
| 4 | P3 | Persistence hint dup with public calculator | Drift | Shared helper | DRY | Same copy |

**Best-practices pass:** Async insights — **good**; charts a11y (legend/tooltip) — verify color-not-only in doughnut.

---

### 3.33 Data extract — `/data-extract` (`DataExtractTool.vue`) — **OK**

Composable-driven panels; drop zone labeled.  
**Self-check:** Large file UX (progress/error); write gate clear for guests vs authed.

---

### 3.34 News sources — `/news/sources` (`NewsSourcesPage.vue`) — **Needs work**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | nestedInteractive keyboard gap | Mouse-only row open | Explicit open control | Keyboard parity | Tab open works |
| 2 | P2 | Error as Card+retry not ErrorState | Inconsistent | Use ErrorState | Shared pattern | Same as NewsAdmin |
| 3 | P3 | ⚠ glyph for fetch error | Prefer icon component + text | SVG + visible text | Color-not-only | Error not color-only |

**Best-practices pass:** After keyboard + ErrorState — **pass**.

---

### 3.35 News article admin — `/news/edit/:id` (`NewsArticleAdminPage.vue`, ~481) — **Priority fix**

| # | Sev | Finding | Why bad | Solution | Why better | Self-check |
|---|-----|---------|---------|----------|------------|------------|
| 1 | P1 | Many placeholder-only fields (slug, title, URLs…) | Dense form with no names | Visible labels on every field | Editable by AT + zoom users | Every input has name |
| 2 | P2 | XL monolith | Hard review | Split SystemFields / ContentFields / Preview | Maintainable | Page <200 lines |
| 3 | P2 | Link sanitization via `newsForms` — keep; ensure UI surfaces invalid URL errors near fields | Silent fail risk | Field-level error text | Fixable validation | Invalid URL shows message |

**Best-practices pass:** Themes checkboxes good — **fail** until labels; then re-pass.

---

### 3.36 News admin manage — `NewsAdminPage.vue` (via `?manage=1`) — **OK**

Skeleton/error/empty/drawer present.  
**Self-check:** Permission gate; ingest actions disabled without write.

---

## 4. Shared components / infrastructure checklist

| Asset | Verdict | Action |
|-------|---------|--------|
| `App.vue` | Strong skip link + main | Fix nested main in cook mode |
| `PageShell` / `PageChrome` | Good h1 pattern | Ensure News article title uses real h1 content |
| `BaseImage` | Lazy good; dual img bad | Skeleton placeholder; CSP-aligned src |
| `BaseInput` | Correct a11y contract | Call sites must supply names |
| `AdminListRow` | nestedInteractive tradeoff | Document + add open control pattern |
| Icons / SVG | Vue SFCs preferred | Replace emoji weather / unicode callback marks |
| `pageSeo` / `useRouteSeo` | Solid | Conditional amphtml; absolute OG in HTML |
| Auth store + API | Cookie session good | Test refresh interceptor |
| Charts | Deferred well | Token sync; per-chart lazy optional |

---

## 5. Prioritized execution backlog (for a future implementation PR — not this draft)

### Wave A — correctness & security (do first)

1. News article visible `<h1>` title (3.11)  
2. AdminSearch hit URL allowlist / same-origin only (3.21)  
3. Feedback: stop auto-archive; stop putting reply body in query string (3.18 + 3.23)  
4. Align `safeImageSrc` ↔ CSP / media proxy (2.2)  
5. DOMPurify hook once (2.4)  
6. Fix nested `<main>` in RecipeCookMode (2.5)

### Wave B — a11y forms & keyboard

1. Label audit across BaseInput call sites (2.1) — NewsArticleAdmin, UrlShortener, VidDownload, AdminSearch, AppLogs, AiChat, Forgot/Settings visible labels  
2. Auth error focus (2.11)  
3. AdminListRow open pattern for nestedInteractive pages (2.6)  
4. Audit/AppLogs disclosure keyboard (3.19–3.20)

### Wave C — DRY & structure

1. AuthPageShell + PasswordFields (2.3)  
2. ToolTileGrid shared (3.8 / 3.16)  
3. Generic ConfirmDialog (3.27)  
4. Split XL pages/composables: Settings, AdminUsers, NewsArticleAdmin, useExpensesTool (3.7, 3.17, 3.35, 3.32)  
5. Standardize list fetching on `useApiAction` (2.10)

### Wave D — performance & media polish

1. BaseImage single-request placeholder (2.2)  
2. Vendor chunking + font strategy (2.7)  
3. Chart theme from CSS variables; optional per-chart import (3.32)  
4. Conditional amphtml + absolute OG (2.8, 2.9)  
5. 404 recovery links (3.14)

### Wave E — tests

1. `passwordPolicy` unit tests  
2. `useApi` refresh queue tests  
3. Auth page smoke tests (token scrub, redirect)  
4. AdminSearch malicious hit URL test  
5. Concurrent `sanitizeEmailHtml` test  

---

## 6. Per-wave verification (definition of done)

After each wave, re-run:

- [ ] `.cursor/references/accessibility-checklist.md` on touched pages  
- [ ] Targeted vitest for changed utils/components  
- [ ] Manual keyboard pass on auth + one admin list + one public tool  
- [ ] Lighthouse (mobile) on `/`, `/news/:slug`, `/recipes` for perf waves  
- [ ] Confirm no secrets in URLs (`sensitiveUrl` scrub still holds)  
- [ ] Confirm Toss tokens still used (no new raw hex in components outside chart bridge until tokens wired)

---

## 7. Out of scope (explicit)

- Backend API redesign, Mongo indexes, Celery, nginx CSP file edits beyond noting the client contract  
- Full AMP HTML rewrite / article AMP generation (server) — only client discovery link called out  
- i18n / multi-language product (none today; `lang="en"` hardcoded — note only)  
- Visual redesign of portfolio brand moments (Toss portfolio exception already allows accents)

---

## 8. Meta self-check of this plan

| Risk of false finding | Mitigation used |
|----------------------|-----------------|
| “No lazy routes” | Verified all routes use dynamic import |
| “JWT in localStorage” | Verified cookie session + guest localStorage only for non-secrets |
| “No AMP at all” | Verified server `/amp` + client amphtml; issue is **mismatched coverage**, not missing portfolio AMP |
| “v-html XSS everywhere” | Only EmailTool; sanitized — issue is hook lifecycle + draft channel, not missing sanitizer |
| “BaseInput ignores a11y” | BaseInput is correct; **call sites** are the bug |
| Ecosystem design DB missing | Noted; recommendations from repo skills/checklists |

**Plan confidence:** High for P0/P1 items with file-level evidence; medium for P3 polish (subjective UX).  

**Next step when approved:** Implement Wave A in a dedicated PR (no drive-by refactors outside the wave list).
