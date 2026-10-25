# Gleb.Y vector logo

Primary mark: golden **open-ring G** + square period + quiet **Y**. Transparent ground.

Working copies here mirror [`../logo-concepts/gy-open-ring/`](../logo-concepts/gy-open-ring/). Older gear concept kept under [`../logo-concepts/gy-gear-circuit/`](../logo-concepts/gy-gear-circuit/).

## Local files

| File | Use |
| --- | --- |
| `lockup.svg` / `lockup-light.svg` | Horizontal G · Y |
| `mark.svg` / `mark-light.svg` | Open-ring G + square period |
| `welcome-bg.svg` / `welcome-bg-light.svg` | Portfolio hero decoration |

## Live use

- App chrome: [`SiteLogo.vue`](../../src/components/brand/SiteLogo.vue) — dark/light SVG by `data-theme` (`gy-mark-simple[-light].svg` / `gy-logo[-light].svg`)
- Favicon / touch icons: dark mark [`client/public/favicon.svg`](../../public/favicon.svg) and PNG/ICO siblings
- Portfolio hero: `welcome-bg[-light].svg` on [`PortfolioPage.vue`](../../src/pages/PortfolioPage.vue) only
- Social card: [`client/public/social-preview.png`](../../public/social-preview.png) (type-only OG until refreshed)

## Deployed (public)

| File | Use |
| --- | --- |
| `gy-logo.svg` / `gy-logo-light.svg` | Full lockup |
| `gy-mark-simple.svg` / `gy-mark-simple-light.svg` | Open-ring mark |
| `welcome-bg.svg` / `welcome-bg-light.svg` | Hero decoration |
| `gy-logo-512.png` | Raster fallback |

Also: `client/public/brand/`, `docs/public/`, `server/app/static/brand/gy-logo-512.png`.
