<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

withDefaults(
  defineProps<{
    to: RouteLocationRaw;
    size?: "default" | "compact";
    label?: string;
  }>(),
  {
    size: "default",
  },
);

const backLabels: Record<string, string> = {
  "/": "Back to portfolio",
  "/admin": "Back to admin tools",
  "/tools": "Back to tools",
  "/news": "Back to news",
};

function backAriaLabel(to: RouteLocationRaw, label?: string): string {
  if (label) return label;
  const path = typeof to === "string" ? to : (to.path ?? "");
  return backLabels[path] ?? "Back";
}
</script>

<template>
  <RouterLink
    :to="to"
    :aria-label="backAriaLabel(to, label)"
    class="inline-flex items-center justify-center rounded-lg border border-surface-border bg-surface-card text-surface-light transition-all duration-200 hover:border-accent-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
    :class="size === 'compact' ? 'h-8 w-8' : 'h-10 w-10'"
  >
    <svg
      :class="size === 'compact' ? 'h-5 w-5' : 'h-10 w-10'"
      viewBox="0 0 40 40"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
    >
      <path d="M24 11 15 20l9 9" />
      <path d="M16 20h18" />
    </svg>
  </RouterLink>
</template>
