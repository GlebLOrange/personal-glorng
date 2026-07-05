<script setup lang="ts">
import { computed } from "vue";

import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import { useNextSectionScroll } from "@/composables/useNextSectionScroll";
import { useScrollProgress } from "@/composables/useScrollProgress";
import { isAiSearchEnabled } from "@/utils/featureFlags";

const { showArrowDown, showToTop } = useScrollProgress();
const { scrollToNextSection, scrollToTop } = useNextSectionScroll();

const arrowDownBottomClass = computed(() =>
  isAiSearchEnabled() ? "bottom-24" : "bottom-6",
);
</script>

<template>
  <button
    v-if="showToTop"
    type="button"
    class="interactive-surface fixed top-32 right-4 md:right-6 z-30 flex size-11 items-center justify-center text-surface-light print:hidden focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
    aria-label="To the top"
    @click="scrollToTop"
  >
    <ScrollArrowIcon direction="up" />
  </button>

  <button
    v-if="showArrowDown"
    type="button"
    :class="[
      'interactive-surface fixed right-6 z-30 flex size-11 items-center justify-center text-surface-light print:hidden focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      arrowDownBottomClass,
    ]"
    aria-label="Scroll to next section"
    @click="scrollToNextSection"
  >
    <ScrollArrowIcon direction="down" />
  </button>
</template>
