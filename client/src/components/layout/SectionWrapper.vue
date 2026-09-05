<script setup lang="ts">
import { computed, useSlots } from "vue";

const props = defineProps<{
  id?: string;
  title?: string;
  dark?: boolean;
  alternate?: boolean;
  /** @deprecated Use width="full" instead */
  centered?: boolean;
  width?: "full" | "content" | "prose";
}>();

const slots = useSlots();

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

const showHeader = computed(() => Boolean(props.title || slots.headerActions));
</script>

<template>
  <section
    :id="id"
    :class="[
      'py-20 md:py-24 px-6 scroll-mt-40 md:scroll-mt-44',
      alternate && 'bg-surface-card/30',
      /* surface-light = primary text in both themes; `dark` kept for call-site compat */
      'text-surface-light',
    ]"
  >
    <div class="page-tile-scope mx-auto w-full max-w-5xl">
      <div v-if="showHeader" class="mb-8 flex min-w-0 flex-wrap items-center justify-between gap-4">
        <h2 v-if="title" class="section-title min-w-0">
          <span aria-hidden="true" class="text-accent-blue">§ </span>
          {{ title }}
        </h2>
        <div v-if="$slots.headerActions" class="flex min-w-0 flex-wrap items-center gap-4">
          <slot name="headerActions" />
        </div>
      </div>
      <div :class="innerClass">
        <slot />
      </div>
    </div>
  </section>
</template>
