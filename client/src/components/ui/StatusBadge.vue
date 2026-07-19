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
</script>

<template>
  <span :class="[sizeClass, 'rounded border', className]">{{ label }}</span>
</template>
