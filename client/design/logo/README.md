# Gleb.Y vector logo

Primary mark: golden **gear G** + period + cool **circuit Y**. Transparent ground.

Working copies here mirror [`../logo-concepts/gy-gear-circuit/`](../logo-concepts/gy-gear-circuit/). Canonical source for deploy: [`logo/vector/`](../../../logo/vector/).

## Local files

| File | Use |
| --- | --- |
| `lockup.svg` / `lockup-light.svg` | Horizontal G · Y |
| `mark.svg` / `mark-light.svg` | Gear-G only |
| `mark-mono.svg` | Single-ink gear |
| `tile.svg` | Gear on dark rounded tile |

## Live use

- App chrome: [`SiteLogo.vue`](../../src/components/brand/SiteLogo.vue) — dark/light SVG by `data-theme` (`gy-mark-simple[-light].svg` / `gy-logo[-light].svg`)
- Favicon / touch icons: dark gear [`client/public/favicon.svg`](../../public/favicon.svg) and PNG/ICO siblings
- Social card: [`client/public/social-preview.png`](../../public/social-preview.png) (type-only OG until refreshed)

## Deployed (`logo/vector/` → public)

| File | Use |
| --- | --- |
| `gy-logo.svg` / `gy-logo-light.svg` | Full lockup |
| `gy-mark-simple.svg` / `gy-mark-simple-light.svg` | Gear mark |
| `gy-logo-512.png` | Raster fallback |

Also: `client/public/brand/`, `docs/public/`, `server/app/static/brand/gy-logo-512.png`.
