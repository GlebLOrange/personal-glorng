<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    label: string;
    className: string;
    size?: "sm" | "md";
  }>(),
  { size: "sm" },
);

const sizeClass = computed(() =>
  props.size === "md" ? "text-sm px-3 py-1" : "text-xs px-2 py-0.5",
);
</script>

<template>
  <span :class="[sizeClass, 'rounded border', className]">{{ label }}</span>
</template>
