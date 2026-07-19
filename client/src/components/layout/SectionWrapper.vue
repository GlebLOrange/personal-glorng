<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  id?: string;
  title?: string;
  dark?: boolean;
  alternate?: boolean;
  /** @deprecated Use width="full" instead */
  centered?: boolean;
  width?: "full" | "content" | "prose";
}>();

const innerClass = computed(() => {
  const resolvedWidth = props.width ?? (props.centered ? "full" : "content");
  if (resolvedWidth === "full") {
    return "w-full";
  }
  if (resolvedWidth === "prose") {
    // Left-align column under section titles (same shell edge); do not center
    return "w-full max-w-3xl";
  }
  return "page-body-narrow w-full";
});
</script>

<template>
  <section
    :id="id"
    :class="[
      'py-20 md:py-24 px-6 scroll-mt-40 md:scroll-mt-44',
      alternate && 'bg-surface-card/30',
      dark ? 'text-surface-light' : 'text-surface-dark',
    ]"
  >
    <div class="page-tile-scope mx-auto w-full max-w-5xl xl:max-w-6xl">
      <h2 v-if="title" class="section-title mb-8">
        <span aria-hidden="true" class="text-accent-blue">§ </span>
        {{ title }}
      </h2>
      <div :class="innerClass">
        <slot />
      </div>
    </div>
  </section>
</template>
