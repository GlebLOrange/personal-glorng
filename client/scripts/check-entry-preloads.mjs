#!/usr/bin/env node
/**
 * Guard: Chart.js must not land on the SPA entry modulepreload list.
 * Run after `vite build` (see package.json `build:check`).
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const indexHtml = join(root, "dist", "index.html");

let html;
try {
  html = readFileSync(indexHtml, "utf8");
} catch {
  console.error(`check-entry-preloads: missing ${indexHtml} — run vite build first`);
  process.exit(1);
}

const preloadHrefs = [...html.matchAll(/rel="modulepreload"[^>]*href="([^"]+)"/g)].map(
  (match) => match[1],
);
const forbidden = /(?:^|\/)(?:charts?|chartTheme|chart\.js|vue-chartjs)[^/]*\.js$/i;
const offenders = preloadHrefs.filter((href) => forbidden.test(href.split("?")[0] ?? href));

if (offenders.length > 0) {
  console.error("check-entry-preloads: chart-related modulepreload on entry:");
  for (const href of offenders) console.error(`  ${href}`);
  process.exit(1);
}

console.log(
  `check-entry-preloads: ok (${preloadHrefs.length} modulepreload link(s), no chart chunks)`,
);
