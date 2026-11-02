# Gleb.Y vector logo

Primary mark: charcoal gear with integrated **Y** and muted-gold **G**. Transparent ground.

Working copies here are the live mark source. Trace from the square source art into `viewBox="0 0 100 100"`.

## Local files

| File | Use |
| --- | --- |
| `mark.svg` / `mark-light.svg` | Square gear Y/G (dark gear on light twin for `#e5e7eb`) |
| `lockup.svg` / `lockup-light.svg` | Legacy horizontal G · Y (superseded by square mark) |

## Live use

- App chrome: [`SiteLogo.vue`](../../src/components/brand/SiteLogo.vue) uses `/favicon.svg` for the dark mark and `/brand/gy-mark-simple-light.svg` for light theme.
- Browser favicon / touch icons: [`client/public/favicon.svg`](../../public/favicon.svg) and PNG/ICO siblings
- Social card: [`client/public/social-preview.png`](../../public/social-preview.png) — mark + “Gleb.Y / Python Backend / FastAPI Engineer” on dark ground

## Palette

| Role | Hex |
| --- | --- |
| Gear / Y (dark surfaces) | `#5a5a5a` |
| Gear / Y (light twin) | `#3d3d3d` |
| Muted-gold G | `#c4a15a` |

## Deployed (public)

| File | Use |
| --- | --- |
| `/favicon.svg` | Canonical dark square mark, shared by app chrome and browser favicon |
| `gy-mark-simple-light.svg` | Light-theme app mark |
| `gy-logo-512.png` | Raster fallback (email, resume) |

Also: `client/public/brand/`, `docs/public/`, `server/app/static/brand/gy-logo-512.png`.
