<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useSlots } from "vue";

import QuestionIcon from "@/components/icons/QuestionIcon.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { Card } from "@/components/ui/card";

const props = defineProps<{
  /** Accessible name + hover helptext for the ? control. */
  title: string;
}>();

const slots = useSlots();
/** Pinned via click; hover opens a transient preview. Both render as an overlay (no reflow). */
const pinned = ref(false);
const hovered = ref(false);
const open = computed(() => pinned.value || hovered.value);
let closeTimer: ReturnType<typeof setTimeout> | null = null;

function clearCloseTimer(): void {
  if (closeTimer !== null) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
}

function showPreview(): void {
  clearCloseTimer();
  hovered.value = true;
}

function scheduleHidePreview(): void {
  clearCloseTimer();
  closeTimer = setTimeout(() => {
    hovered.value = false;
    closeTimer = null;
  }, 150);
}

function toggle(): void {
  clearCloseTimer();
  pinned.value = !pinned.value;
  if (!pinned.value) hovered.value = false;
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && open.value) {
    pinned.value = false;
    hovered.value = false;
  }
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onBeforeUnmount(() => {
  clearCloseTimer();
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div class="relative w-full min-w-0 max-w-full">
    <div class="mb-4 flex w-full min-w-0 flex-wrap items-center gap-2">
      <div v-if="slots.start" class="min-w-0 flex-1 overflow-hidden">
        <slot name="start" />
      </div>
      <div class="flex shrink-0 items-center gap-2" :class="slots.start ? 'ml-auto' : undefined">
        <slot name="actions" />
        <span
          class="relative inline-flex shrink-0"
          @mouseenter="showPreview"
          @mouseleave="scheduleHidePreview"
        >
          <ToolbarPillButton
            action="create"
            :icon="false"
            class="!w-10 !min-w-10 !px-0"
            :aria-label="props.title"
            :title="props.title"
            :aria-expanded="open"
            @click="toggle"
            @focus="showPreview"
            @blur="scheduleHidePreview"
          >
            <QuestionIcon class-name="size-3.5" />
          </ToolbarPillButton>
        </span>
      </div>
    </div>

    <!-- Overlay: absolutely positioned so opening never pushes content below. -->
    <Card
      v-if="open"
      role="dialog"
      :aria-label="props.title"
      class="absolute left-0 right-0 top-full z-40 -mt-2 max-h-[70vh] w-full min-w-0 max-w-full overflow-auto break-words shadow-lg [overflow-wrap:anywhere]"
      @mouseenter="showPreview"
      @mouseleave="scheduleHidePreview"
    >
      <div class="min-w-0 max-w-full">
        <slot />
      </div>
    </Card>
  </div>
</template>
