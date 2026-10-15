<script setup lang="ts">
import { computed } from "vue";

import { colorThemeResolved } from "@/composables/useColorTheme";

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

const src = computed(() => {
  const light = colorThemeResolved.value === "light";
  if (props.variant === "full") {
    return light ? "/brand/gy-logo-light.svg" : "/brand/gy-logo.svg";
  }
  return light ? "/brand/gy-mark-simple-light.svg" : "/brand/gy-mark-simple.svg";
});
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
