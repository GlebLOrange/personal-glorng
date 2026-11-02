#!/usr/bin/env node
/**
 * Fail when the main Tailwind entry CSS grows beyond budget (render-blocking on `/`).
 * Run after `vite build` (see package.json `build:check`).
 */
import { readdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const assetsDir = join(root, "dist", "assets");

/** Raw bytes ceiling for index-*.css (gzip ~17 KB today). */
const MAX_INDEX_CSS_BYTES = 132 * 1024;

let entries;
try {
  entries = readdirSync(assetsDir);
} catch {
  console.error(`check-css-budget: missing ${assetsDir} — run vite build first`);
  process.exit(1);
}

const indexCss = entries.find((name) => /^index-.*\.css$/.test(name));
if (!indexCss) {
  console.error("check-css-budget: no index-*.css in dist/assets");
  process.exit(1);
}

const path = join(assetsDir, indexCss);
const bytes = statSync(path).size;
if (bytes > MAX_INDEX_CSS_BYTES) {
  console.error(
    `check-css-budget: ${indexCss} is ${bytes} bytes (max ${MAX_INDEX_CSS_BYTES})`,
  );
  process.exit(1);
}

console.log(`check-css-budget: ok (${indexCss} ${bytes} bytes ≤ ${MAX_INDEX_CSS_BYTES})`);
