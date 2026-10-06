# Gleb.Y vector logo

Commissioned graffiti sticker-badge **GY** monogram (gears + wrench). Source files live in [`logo/vector/`](../../../logo/vector/).

## Live use

- App chrome: [`SiteLogo.vue`](../../src/components/brand/SiteLogo.vue) (nav + footer + hero) — `/brand/gy-mark-simple.svg` or `/brand/gy-logo.svg`
- Favicon / touch icons: [`client/public/favicon.svg`](../../public/favicon.svg) and PNG/ICO siblings
- Social card: [`client/public/social-preview.png`](../../public/social-preview.png)

## Source files (`logo/vector/`)

| File | Use |
| --- | --- |
| `gy-logo.svg` | Full-color logo, transparent ground |
| `gy-mark-simple.svg` | Simplified mark for favicon and small UI |
| `gy-logo-512.png` | Raster fallback (email, PDF embed) |

## Deployed copies

Static assets are copied to `client/public/brand/` and favicon files at `client/public/` for Vite/nginx.
