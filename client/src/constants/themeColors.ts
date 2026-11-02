/**
 * Browser `theme-color` per theme — single source of truth.
 * Must equal `--palette-theme-color` in styles/main.css and the FOUC script in
 * index.html (enforced by themeColors.test.ts).
 */
export const THEME_COLOR = {
  dark: "#141218",
  light: "#fef7ff",
} as const;
