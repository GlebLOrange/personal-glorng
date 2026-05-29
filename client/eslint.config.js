import js from "@eslint/js";
import pluginVue from "eslint-plugin-vue";
import tseslint from "typescript-eslint";
import vueTsConfig from "@vue/eslint-config-typescript";
import prettier from "eslint-config-prettier";

export default tseslint.config(
  {
    ignores: [
      "dist/**",
      "node_modules/**",
      ".vite/**",
      "playwright-report/**",
      "test-results/**",
    ],
  },
  js.configs.recommended,
  ...pluginVue.configs["flat/recommended"],
  ...vueTsConfig(),
  prettier,
  {
    files: ["**/*.{ts,vue}"],
    rules: {
      "vue/multi-word-component-names": "off",
      "vue/require-default-prop": "warn",
      "vue/attributes-order": "warn",
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
    },
  },
);
