import { sentryVitePlugin } from "@sentry/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { visualizer } from "rollup-plugin-visualizer";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // .env.* is not auto-injected into process.env inside vite.config — load explicitly.
  const env = loadEnv(mode, process.cwd(), "");
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
            if (id.includes("node_modules/chart.js") || id.includes("node_modules/vue-chartjs")) {
              return "charts";
            }
            if (id.includes("node_modules/firebase")) {
              return "firebase";
            }
            if (
              id.includes("node_modules/vue/") ||
              id.includes("node_modules/@vue/") ||
              id.includes("node_modules/vue-router") ||
              id.includes("node_modules/pinia")
            ) {
              return "vue-vendor";
            }
          },
        },
      },
    },
    plugins: [
      vue(),
      tailwindcss(),
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
