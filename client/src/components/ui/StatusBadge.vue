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
  if (props.size === "lg") return "text-lg font-bold px-3 py-1";
  if (props.size === "md") return "text-sm px-3 py-1";
  return "text-xs px-2 py-0.5";
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
