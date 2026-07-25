<script setup lang="ts">
import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { useNextSectionScroll } from "@/composables/useNextSectionScroll";
import { useScrollProgress } from "@/composables/useScrollProgress";

const { showArrowDown, showToTop } = useScrollProgress();
const { scrollToNextSection, scrollToTop } = useNextSectionScroll();
</script>

<template>
  <ToolbarPillButton
    v-if="showToTop"
    family="1xx"
    type="button"
    class="fixed top-32 right-4 z-30 size-11 !px-0 md:right-6 print:hidden mr-[env(safe-area-inset-right)]"
    aria-label="To the top"
    @click="scrollToTop"
  >
    <ScrollArrowIcon direction="up" />
  </ToolbarPillButton>

  <ToolbarPillButton
    v-if="showArrowDown"
    family="1xx"
    type="button"
    class="fixed right-6 bottom-6 z-30 size-11 !px-0 print:hidden mb-[env(safe-area-inset-bottom)] mr-[env(safe-area-inset-right)]"
    aria-label="Scroll to next section"
    @click="scrollToNextSection"
  >
    <ScrollArrowIcon direction="down" />
  </ToolbarPillButton>
</template>
