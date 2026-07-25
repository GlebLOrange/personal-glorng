<script setup lang="ts">
import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import { useNextSectionScroll } from "@/composables/useNextSectionScroll";
import { useScrollProgress } from "@/composables/useScrollProgress";

const { showArrowDown, showToTop } = useScrollProgress();
const { scrollToNextSection, scrollToTop } = useNextSectionScroll();
</script>

<template>
  <!-- Content-column rail: buttons sit just outside the padded max-w edge. -->
  <div v-if="showToTop" class="pointer-events-none fixed inset-x-0 top-32 z-30 print:hidden">
    <div class="relative mx-auto w-full max-w-5xl px-6 xl:max-w-6xl">
      <IconActionButton
        family="1xx"
        type="button"
        class="pointer-events-auto absolute right-0 translate-x-2 mr-[env(safe-area-inset-right)]"
        aria-label="To the top"
        @click="scrollToTop"
      >
        <ScrollArrowIcon direction="up" />
      </IconActionButton>
    </div>
  </div>

  <div
    v-if="showArrowDown"
    class="pointer-events-none fixed inset-x-0 bottom-6 z-30 print:hidden mb-[env(safe-area-inset-bottom)]"
  >
    <div class="relative mx-auto w-full max-w-5xl px-6 xl:max-w-6xl">
      <IconActionButton
        family="1xx"
        type="button"
        class="pointer-events-auto absolute right-0 translate-x-2 mr-[env(safe-area-inset-right)]"
        aria-label="Scroll to next section"
        @click="scrollToNextSection"
      >
        <ScrollArrowIcon direction="down" />
      </IconActionButton>
    </div>
  </div>
</template>
