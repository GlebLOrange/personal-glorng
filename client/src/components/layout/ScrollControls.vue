<script setup lang="ts">
import ScrollArrowIcon from "@/components/icons/ScrollArrowIcon.vue";
import BackLink from "@/components/ui/BackLink.vue";
import IconActionButton from "@/components/ui/IconActionButton.vue";
import { useNextSectionScroll } from "@/composables/useNextSectionScroll";
import { usePageBackTo } from "@/composables/usePageBackTo";
import { useScrollProgress } from "@/composables/useScrollProgress";

const { showArrowDown, showToTop } = useScrollProgress();
const { scrollToNextSection, scrollToTop } = useNextSectionScroll();
const { backTo } = usePageBackTo();
</script>

<template>
  <!-- Rail matches shell; scroll buttons sit in the gutter past the right edge.
       Below 1180px they pin to the viewport edge; page-shell reserves end padding so content is never covered. -->
  <div v-if="showToTop" class="pointer-events-none fixed inset-x-0 top-[14%] z-30 print:hidden">
    <div class="relative mx-auto w-full max-w-5xl px-6">
      <IconActionButton
        action="create"
        type="button"
        class="scroll-rail-end pointer-events-auto"
        aria-label="to the top"
        @click="scrollToTop"
      >
        <ScrollArrowIcon direction="up" />
      </IconActionButton>
    </div>
  </div>

  <!-- One bottom rail: Back (left, aligned with breadcrumbs) + scroll-to-next (right gutter). -->
  <div
    v-if="backTo || showArrowDown"
    data-testid="page-bottom-rail"
    class="page-bottom-rail pointer-events-none fixed inset-x-0 bottom-[8%] z-30 print:hidden"
  >
    <div class="relative mx-auto flex h-11 w-full max-w-5xl items-center justify-start px-6">
      <BackLink v-if="backTo" :to="backTo" class="pointer-events-auto" />
      <IconActionButton
        v-if="showArrowDown"
        action="create"
        type="button"
        class="scroll-rail-end pointer-events-auto"
        aria-label="scroll to next section"
        @click="scrollToNextSection"
      >
        <ScrollArrowIcon direction="down" />
      </IconActionButton>
    </div>
  </div>
</template>
