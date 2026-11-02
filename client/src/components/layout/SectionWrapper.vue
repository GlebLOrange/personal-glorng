<script setup lang="ts">
import { computed, useSlots } from "vue";

/** M3 chromatic roles for portfolio section-name pills. */
export type SectionLabelTone = "primary" | "secondary" | "tertiary" | "error" | "custom";

const props = defineProps<{
  id?: string;
  title?: string;
  alternate?: boolean;
  width?: "full" | "content" | "prose";
  /** Portfolio-only: colorful overlapping section name pill + border frame. */
  labelTone?: SectionLabelTone;
}>();

const slots = useSlots();

const innerClass = computed(() => {
  const resolvedWidth = props.width ?? "content";
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
const useLabelPill = computed(() => Boolean(props.labelTone && props.title));

const pillClass = computed(() => [
  "section-label-pill",
  props.labelTone ? `section-label-pill--${props.labelTone}` : "",
]);
</script>

<template>
  <section
    :id="id"
    :class="[
      useLabelPill
        ? 'scroll-mt-40 px-6 py-12 md:scroll-mt-44 md:py-14'
        : 'scroll-mt-40 px-6 py-20 md:scroll-mt-44 md:py-24',
      alternate && !useLabelPill && 'bg-surface-card/30',
      'text-surface-light',
    ]"
  >
    <div class="page-tile-scope mx-auto w-full max-w-5xl">
      <div
        v-if="useLabelPill"
        class="relative rounded-2xl border border-surface-border px-6 pb-6 pt-8 md:px-8 md:pb-8 md:pt-10"
      >
        <div class="absolute top-0 left-6 z-10 -translate-y-1/2 md:left-8">
          <h2 :class="pillClass">
            {{ title }}
          </h2>
        </div>
        <div
          v-if="$slots.headerActions"
          class="mb-4 flex min-w-0 flex-wrap items-center justify-end gap-4"
        >
          <slot name="headerActions" />
        </div>
        <div :class="innerClass">
          <slot />
        </div>
      </div>

      <template v-else>
        <div
          v-if="showHeader"
          class="mb-8 flex min-w-0 flex-wrap items-center justify-between gap-4"
        >
          <h2 v-if="title" class="section-title min-w-0">
            {{ title }}
          </h2>
          <div v-if="$slots.headerActions" class="flex min-w-0 flex-wrap items-center gap-4">
            <slot name="headerActions" />
          </div>
        </div>
        <div :class="innerClass">
          <slot />
        </div>
      </template>
    </div>
  </section>
</template>
