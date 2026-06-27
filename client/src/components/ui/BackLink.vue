<script setup lang="ts">
import type { RouteLocationRaw } from "vue-router";

withDefaults(
  defineProps<{
    to: RouteLocationRaw;
    label?: string;
  }>(),
  {
    label: "BACK",
  },
);
</script>

<template>
  <RouterLink
    :to="to"
    :aria-label="label"
    class="group relative inline-flex h-10 w-10 items-center justify-center rounded-lg border border-surface-border bg-surface-card text-surface-light transition-all duration-200 hover:border-accent-blue focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
  >
    <svg
      class="h-10 w-10"
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
    <span
      aria-hidden="true"
      class="pointer-events-none absolute right-0 top-full z-10 mt-2 rounded-md border border-surface-border bg-surface-card px-2 py-1 text-xs font-medium text-surface-light opacity-0 shadow-lg transition-opacity duration-150 group-hover:opacity-100 group-focus-visible:opacity-100"
    >
      {{ label }}
    </span>
  </RouterLink>
</template>
