<script setup lang="ts">
import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import { useNextSectionScroll } from "@/composables/useNextSectionScroll";
import { useScrollProgress } from "@/composables/useScrollProgress";

const { showArrowDown, showToTop } = useScrollProgress();
const { scrollToNextSection, scrollToTop } = useNextSectionScroll();
</script>

<template>
  <!-- Rail matches shell; buttons sit in the gutter past the right edge -->
  <div v-if="showToTop" class="pointer-events-none fixed inset-x-0 top-[14%] z-30 print:hidden">
    <div class="relative mx-auto w-full max-w-5xl px-6">
      <IconActionButton
        family="1xx"
        type="button"
        class="shell-outside-end pointer-events-auto"
        aria-label="To the top"
        @click="scrollToTop"
      >
        <ScrollArrowIcon direction="up" />
      </IconActionButton>
    </div>
  </div>

  <div
    v-if="showArrowDown"
    class="pointer-events-none fixed inset-x-0 bottom-[14%] z-30 print:hidden"
  >
    <div class="relative mx-auto w-full max-w-5xl px-6">
      <IconActionButton
        family="1xx"
        type="button"
        class="shell-outside-end pointer-events-auto"
        aria-label="Scroll to next section"
        @click="scrollToNextSection"
      >
        <ScrollArrowIcon direction="down" />
      </IconActionButton>
    </div>
  </div>
</template>
