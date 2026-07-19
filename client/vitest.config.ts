import { fileURLToPath, URL } from "node:url";
import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  test: {
    environment: "happy-dom",
    include: ["src/**/*.test.ts"],
    clearMocks: true,
    coverage: {
      provider: "v8",
      reporter: ["text", "text-summary"],
      // Gate the areas unit tests actually exercise (not every page SFC).
      include: [
        "src/components/ui/**/*.{ts,vue}",
        "src/composables/**/*.ts",
        "src/utils/**/*.ts",
        "src/stores/**/*.ts",
        "src/platform/**/*.ts",
      ],
      exclude: ["src/**/*.test.ts", "src/**/*.d.ts"],
      thresholds: {
        // Baseline ~27% on P0 suite; floor leaves headroom for churn.
        statements: 25,
      },
    },
  },
});
