<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    label: string;
    className: string;
    size?: "sm" | "md" | "lg";
    /** Keep badge at least as wide as the longest of these labels (filter options). */
    fitLabels?: string[];
  }>(),
  { size: "sm", fitLabels: undefined },
);

const sizeClass = computed(() => {
  if (props.size === "lg") return "items-center text-lg font-bold px-3 py-1 leading-none";
  if (props.size === "md") return "items-center text-sm px-3 py-1 leading-none";
  // Match AdminFilterChip vertical rhythm (same status paint language).
  return "items-center px-2 py-1 text-xs leading-normal";
});

/** Display-only — borders belong on clickable/action controls. */
const toneClass = computed(() =>
  props.className
    .split(/\s+/)
    .filter((token) => token && !token.startsWith("border-"))
    .join(" "),
);

const longestFitLabel = computed(() => {
  const labels = props.fitLabels;
  if (!labels?.length) return null;
  return labels.reduce((longest, label) => (label.length > longest.length ? label : longest));
});

const rootClass = computed(() => [
  sizeClass.value,
  longestFitLabel.value ? "inline-grid justify-items-center" : "inline-flex",
  "rounded ring-1 ring-inset ring-current/35",
  toneClass.value,
]);
</script>

<template>
  <span v-if="longestFitLabel" :class="rootClass">
    <span class="invisible col-start-1 row-start-1 whitespace-nowrap" aria-hidden="true">
      {{ longestFitLabel }}
    </span>
    <span class="col-start-1 row-start-1 whitespace-nowrap">{{ label }}</span>
  </span>
  <span v-else :class="rootClass">{{ label }}</span>
</template>
