<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    label: string;
    className: string;
    size?: "sm" | "md" | "lg";
  }>(),
  { size: "sm" },
);

const sizeClass = computed(() => {
  if (props.size === "lg") return "inline-flex items-center text-lg font-bold px-3 py-1 leading-none";
  if (props.size === "md") return "inline-flex items-center text-sm px-3 py-1 leading-none";
  // Match AdminFilterChip vertical rhythm (same status paint language).
  return "inline-flex items-center px-2 py-1 text-xs leading-normal";
});

/** Display-only — borders belong on clickable/action controls. */
const toneClass = computed(() =>
  props.className
    .split(/\s+/)
    .filter((token) => token && !token.startsWith("border-"))
    .join(" "),
);
</script>

<template>
  <span :class="[sizeClass, 'rounded', toneClass]">{{ label }}</span>
</template>
