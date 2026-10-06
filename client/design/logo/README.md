# Gleb.Y vector logo

Period-hinge mark: a geometric **G** whose right opening is the fork of a **Y**, with the brand period in the hinge.

## Live use

- App chrome: [`SiteLogo.vue`](../../src/components/brand/SiteLogo.vue) (nav + footer) — ink `currentColor`, period `--color-accent-blue`
- Favicon / PWA icons: [`client/public/favicon.svg`](../../public/favicon.svg) and raster siblings from `tile.svg`
- Social card: [`client/public/social-preview.png`](../../public/social-preview.png)

## Source files

| File | Use |
| --- | --- |
| `mark.svg` | Symbol, ink + accent period (transparent ground) |
| `mark-mono.svg` | Same geometry, `currentColor` (export / print) |
| `lockup.svg` | Mark + outlined **Gleb.Y** |
| `tile.svg` | Mark on rounded `#0d1117` (favicon source) |

## Colors (dark theme tokens)

- Ink: `#e6edf3` (`surface-light`)
- Accent period: `#e8b07a` (`accent-blue` / pale orange)
- Tile ground: `#0d1117` (`surface-dark`)

Light UI: prefer `SiteLogo` (or `mark-mono.svg` with local text color).
