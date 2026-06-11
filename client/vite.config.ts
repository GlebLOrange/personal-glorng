import { sentryVitePlugin } from "@sentry/vite-plugin";
import tailwindcss from "@tailwindcss/vite";
import vue from "@vitejs/plugin-vue";
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";

const apiProxyTarget = process.env.VITE_API_PROXY_TARGET ?? "http://server:8000";
const behindNginx = process.env.VITE_BEHIND_NGINX === "true";
const sentryEnabled = Boolean(process.env.SENTRY_AUTH_TOKEN);

export default defineConfig({
  build: {
    sourcemap: sentryEnabled ? "hidden" : false,
  },
  plugins: [
    vue(),
    tailwindcss(),
    sentryVitePlugin({
      org: process.env.SENTRY_ORG,
      project: process.env.SENTRY_PROJECT,
      authToken: process.env.SENTRY_AUTH_TOKEN,
      disable: !sentryEnabled,
    }),
  ],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    host: "0.0.0.0",
    port: 3000,
    // HMR through nginx on :80 when the client runs in Docker behind nginx.
    hmr: behindNginx ? { clientPort: 80 } : undefined,
    proxy: {
      "/api": {
        target: apiProxyTarget,
        changeOrigin: true,
      },
    },
  },
});
