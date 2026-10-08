<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    /** `mark` for chrome/favicon scale; `full` for hero and large brand moments. */
    variant?: "mark" | "full";
    /** Tailwind size classes (default h-9 w-auto ≈ 36px mark height). */
    className?: string;
  }>(),
  {
    variant: "mark",
    className: "h-9 w-auto",
  },
);

const src = computed(() =>
  props.variant === "full" ? "/brand/gy-logo.svg" : "/brand/gy-mark-simple.svg",
);
</script>

<template>
  <img
    :src="src"
    alt=""
    aria-hidden="true"
    :class="className"
    width="36"
    height="36"
    decoding="async"
  />
</template>
