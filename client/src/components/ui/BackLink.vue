<script setup lang="ts">
import { computed } from "vue";
import type { RouteLocationRaw } from "vue-router";

import { actionFamilyClass } from "@/constants/httpStatusColors";

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
    ? "!min-h-8 !min-w-8 !h-8 !w-8"
    : "!min-h-11 !min-w-11 !h-11 !w-11",
);

const iconClass = computed(() => (props.size === "compact" ? "size-4" : "size-5"));

function linkClass(isActive: boolean): string {
  return [
    actionFamilyClass("1xx", isActive),
    // Borderless icon control; anchors ignore :enabled so mirror 1xx hover without it.
    "!border-transparent hover:!border-transparent focus-visible:!border-transparent !px-0",
    isActive ? "" : "hover:text-accent-blue hover:bg-accent-blue/15",
    sizeClass.value,
  ]
    .filter(Boolean)
    .join(" ");
}
</script>

<template>
  <RouterLink v-slot="{ href, navigate, isActive }" :to="to" custom>
    <a
      :href="href"
      :aria-label="backAriaLabel(to, label)"
      :class="linkClass(isActive)"
      @click="navigate($event)"
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
    </a>
  </RouterLink>
</template>
