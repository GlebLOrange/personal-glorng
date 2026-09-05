<script setup lang="ts">
import { onBeforeUnmount, ref, useSlots } from "vue";

import QuestionIcon from "@/components/icons/QuestionIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";

const props = defineProps<{
  /** Accessible name + hover helptext for the ? control. */
  title: string;
}>();

const slots = useSlots();
const open = ref(false);
const hintOpen = ref(false);
let hintCloseTimer: ReturnType<typeof setTimeout> | null = null;

function clearHintTimer(): void {
  if (hintCloseTimer !== null) {
    clearTimeout(hintCloseTimer);
    hintCloseTimer = null;
  }
}

function showHint(): void {
  clearHintTimer();
  if (!open.value) hintOpen.value = true;
}

function scheduleHideHint(): void {
  clearHintTimer();
  hintCloseTimer = setTimeout(() => {
    hintOpen.value = false;
    hintCloseTimer = null;
  }, 120);
}

function toggle(): void {
  clearHintTimer();
  hintOpen.value = false;
  open.value = !open.value;
}

onBeforeUnmount(() => {
  clearHintTimer();
});
</script>

<template>
  <div>
    <div class="mb-4 flex w-full min-w-0 flex-wrap items-center gap-2">
      <slot name="start" />
      <div
        class="flex min-w-0 flex-wrap items-center gap-2"
        :class="slots.start ? 'ml-auto' : undefined"
      >
        <slot name="actions" />
        <span
          class="relative inline-flex shrink-0"
          @mouseenter="showHint"
          @mouseleave="scheduleHideHint"
        >
          <ToolbarPillButton
            family="1xx"
            class="!w-10 !min-w-10 !px-0"
            :aria-label="props.title"
            :aria-expanded="open"
            @click="toggle"
            @focus="showHint"
            @blur="scheduleHideHint"
          >
            <QuestionIcon class-name="size-3.5" />
          </ToolbarPillButton>
          <span
            role="tooltip"
            class="absolute top-full z-20 mt-1 w-max max-w-[min(100vw-2rem,18rem)] rounded-md border border-surface-border bg-surface-card px-2.5 py-1.5 text-xs lowercase leading-normal text-surface-mid shadow-lg"
            :class="[slots.start ? 'right-0' : 'left-0', hintOpen && !open ? undefined : 'sr-only']"
          >
            {{ props.title }}
          </span>
        </span>
      </div>
    </div>

    <Card v-if="open">
      <slot />
    </Card>
  </div>
</template>
