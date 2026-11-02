<script setup lang="ts">
import { computed } from "vue";

import { colorThemeResolved } from "@/composables/useColorTheme";

const props = withDefaults(
  defineProps<{
    /** `mark` for chrome/favicon scale; `full` for hero and large brand moments. */
    variant?: "mark" | "full";
    /** Tailwind size classes (default h-9 w-auto ≈ 36px mark height). */
    className?: string;
    /** Hero LCP hint — maps to fetchpriority="high". */
    priority?: boolean;
  }>(),
  {
    variant: "mark",
    className: "h-9 w-auto",
    priority: false,
  },
);

const isFull = computed(() => props.variant === "full");

const src = computed(() => {
  const light = colorThemeResolved.value === "light";
  if (isFull.value) {
    return light ? "/brand/gy-logo-light.svg" : "/brand/gy-logo.svg";
  }
  return light ? "/brand/gy-mark-simple-light.svg" : "/brand/gy-mark-simple.svg";
});

/** Intrinsic size matches SVG viewBox (square mark 100×100 for mark and full). */
const intrinsicWidth = 100;
const intrinsicHeight = 100;

const imgClass = computed(() => [props.className, "aspect-square"]);
</script>

<template>
  <img
    :src="src"
    alt=""
    aria-hidden="true"
    :class="imgClass"
    :width="intrinsicWidth"
    :height="intrinsicHeight"
    decoding="async"
    :fetchpriority="priority ? 'high' : undefined"
  />
</template>
