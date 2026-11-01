import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { THEME_COLOR } from "./themeColors";

const root = resolve(__dirname, "../..");
const css = readFileSync(resolve(root, "src/styles/main.css"), "utf8");
const html = readFileSync(resolve(root, "index.html"), "utf8");

function block(selector: string): string {
  const start = css.indexOf(selector);
  return css.slice(start, css.indexOf("\n}", start));
}
function token(b: string, name: string): string {
  const m = b.match(new RegExp(`--palette-${name}:\\s*(#[0-9a-fA-F]{6})`));
  if (!m) throw new Error(`missing ${name}`);
  return m[1];
}
function lum(hex: string): number {
  const c = [1, 3, 5]
    .map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function ratio(a: string, b: string): number {
  const [x, y] = [lum(a), lum(b)];
  return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05);
}

const themes = { dark: block(":root,"), light: block('html[data-theme="light"] {') };

describe("theme tokens", () => {
  for (const [name, b] of Object.entries(themes)) {
    it(`${name}: muted text meets AA on page and card`, () => {
      const muted = token(b, "surface-muted");
      expect(ratio(muted, token(b, "surface-dark"))).toBeGreaterThanOrEqual(4.5);
      expect(ratio(muted, token(b, "surface-card"))).toBeGreaterThanOrEqual(4.5);
    });
    it(`${name}: theme-color matches constant and index.html`, () => {
      const c = THEME_COLOR[name as "dark" | "light"];
      expect(token(b, "theme-color")).toBe(c);
      expect(html).toContain(c);
    });
  }
});
