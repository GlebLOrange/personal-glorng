import { sentryVitePlugin } from "@sentry/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { visualizer } from "rollup-plugin-visualizer";
import { defineConfig, loadEnv } from "vite";

import { buildShellHeroHtml } from "./src/utils/shellHero.ts";

function applyRepoRootViteEnv(mode: string): Record<string, string> {
  const repoRoot = fileURLToPath(new URL("..", import.meta.url));
  const clientDir = fileURLToPath(new URL(".", import.meta.url));
  const rootEnv = loadEnv(mode, repoRoot, "VITE_");
  for (const [key, value] of Object.entries(rootEnv)) {
    if (!process.env[key]) process.env[key] = value;
  }
  return { ...rootEnv, ...loadEnv(mode, clientDir, "") };
}

function resolvePublicOrigin(mode: string, env: Record<string, string>): string {
  const fromEnv =
    env.VITE_PUBLIC_ORIGIN?.trim() ||
    process.env.VITE_PUBLIC_ORIGIN?.trim() ||
    loadEnv(mode, fileURLToPath(new URL("..", import.meta.url)), "").BASE_URL?.trim() ||
    "";
  const origin = fromEnv.replace(/\/$/, "");
  if (mode !== "production") {
    return origin || "http://localhost:3000";
  }
  if (!origin) {
    throw new Error(
      "Production build requires VITE_PUBLIC_ORIGIN (or BASE_URL) to the public HTTPS site origin — " +
        "Open Graph URLs in index.html must not default to localhost.",
    );
  }
  const lower = origin.toLowerCase();
  if (lower.includes("localhost") || lower.includes("127.0.0.1")) {
    throw new Error(
      `Production build refuses localhost VITE_PUBLIC_ORIGIN/BASE_URL (${origin}). ` +
        "Set the real public HTTPS origin before vite build.",
    );
  }
  if (!lower.startsWith("https://")) {
    throw new Error(
      `Production build requires an HTTPS VITE_PUBLIC_ORIGIN/BASE_URL (got ${origin}).`,
    );
  }
  return origin;
}

export default defineConfig(({ mode }) => {
  // Client .env.* plus repo-root VITE_* (root .env is not Vite's default envDir).
  const env = applyRepoRootViteEnv(mode);
  const apiProxyTarget =
    env.VITE_API_PROXY_TARGET || process.env.VITE_API_PROXY_TARGET || "http://127.0.0.1:8000";
  const behindNginx =
    env.VITE_BEHIND_NGINX === "true" || process.env.VITE_BEHIND_NGINX === "true";
  const sentryEnabled = Boolean(process.env.SENTRY_AUTH_TOKEN || env.SENTRY_AUTH_TOKEN);
  const analyzeBundle = process.env.ANALYZE === "true" || env.ANALYZE === "true";

  return {
    build: {
      sourcemap: sentryEnabled ? "hidden" : false,
      rollupOptions: {
        output: {
          manualChunks(id) {
            // Do not force chart.js into a named chunk: with Vite 8/Rolldown that
            // shared chunk pulls Vue into it and index.html modulepreloads ~265KB on `/`.
            // Chart components already use defineAsyncComponent.
            if (
              id.includes("node_modules/vue/") ||
              id.includes("node_modules/@vue/") ||
              id.includes("node_modules/vue-router") ||
              id.includes("node_modules/pinia")
            ) {
              return "vue-vendor";
            }
            if (id.includes("node_modules/firebase")) {
              return "firebase";
            }
            if (id.includes("node_modules/dompurify")) {
              return "dompurify";
            }
            if (id.includes("node_modules/vanilla-cookieconsent")) {
              return "cookieconsent";
            }
          },
        },
      },
    },
    plugins: [
      vue(),
      tailwindcss(),
      {
        name: "html-public-origin",
        transformIndexHtml(html) {
          const origin = resolvePublicOrigin(mode, env);
          const hero = buildShellHeroHtml();
          return html
            .replaceAll("__PUBLIC_ORIGIN__", origin)
            .replace('<div id="app"></div>', `<div id="app">${hero}</div>`);
        },
      },
      sentryVitePlugin({
        org: process.env.SENTRY_ORG || env.SENTRY_ORG,
        project: process.env.SENTRY_PROJECT || env.SENTRY_PROJECT,
        authToken: process.env.SENTRY_AUTH_TOKEN || env.SENTRY_AUTH_TOKEN,
        disable: !sentryEnabled,
      }),
      analyzeBundle &&
        visualizer({
          filename: "dist/stats.html",
          gzipSize: true,
          open: false,
        }),
    ].filter(Boolean),
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    server: {
      host: "0.0.0.0",
      port: 3000,
      // HMR through nginx on :80 when browsing via http://localhost (dev-lite).
      hmr: behindNginx ? { clientPort: 80 } : undefined,
      proxy: {
        "/api": {
          target: apiProxyTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
