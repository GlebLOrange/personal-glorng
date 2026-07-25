<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

const props = withDefaults(
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
  "/admin": "Back to admin",
  "/tools": "Back to tools",
  "/news": "Back to news",
};

function backAriaLabel(to: RouteLocationRaw, label?: string): string {
  if (label) return label;
  const path = typeof to === "string" ? to : (to.path ?? "");
  return backLabels[path] ?? "Back";
}

const sizeClass = computed(() =>
  props.size === "compact"
    ? "min-h-9 min-w-9 h-9 w-9"
    : "min-h-11 min-w-11 h-11 w-11",
);

const iconClass = computed(() => (props.size === "compact" ? "h-4 w-4" : "h-5 w-5"));
</script>

<template>
  <RouterLink
    :to="to"
    :aria-label="backAriaLabel(to, label)"
    class="inline-flex items-center justify-center rounded-lg bg-surface-card text-surface-light transition-all duration-200 hover:bg-accent-blue/15 hover:text-accent-blue active:bg-accent-blue/25 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
    :class="sizeClass"
  >
    <svg
      :class="iconClass"
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
