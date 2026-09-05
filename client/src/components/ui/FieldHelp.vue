<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useId, useTemplateRef, watch } from "vue";

import QuestionIcon from "@/components/icons/QuestionIcon.vue";

const props = withDefaults(
  defineProps<{
    /** Help copy shown in the popover; also exposed to assistive tech via contentId. */
    text: string;
    /** Optional id for the help content (for aria-describedby). */
    contentId?: string;
    /** Tooltip edge alignment relative to the ? control. */
    align?: "start" | "end";
  }>(),
  { align: "start" },
);

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");
const fallbackId = useId();
const panelId = computed(() => props.contentId ?? `field-help-${fallbackId}`);

let closeTimer: ReturnType<typeof setTimeout> | null = null;

function clearCloseTimer(): void {
  if (closeTimer !== null) {
    clearTimeout(closeTimer);
    closeTimer = null;
  }
}

function show(): void {
  clearCloseTimer();
  open.value = true;
}

function scheduleHide(): void {
  clearCloseTimer();
  closeTimer = setTimeout(() => {
    open.value = false;
    closeTimer = null;
  }, 120);
}

function hide(): void {
  clearCloseTimer();
  open.value = false;
}

function toggle(): void {
  clearCloseTimer();
  open.value = !open.value;
}

function onDocumentPointerDown(event: PointerEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  if (!root) return;
  if (event.target instanceof Node && root.contains(event.target)) return;
  hide();
}

function onDocumentKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && open.value) {
    event.stopPropagation();
    hide();
  }
}

onMounted(() => {
  document.addEventListener("pointerdown", onDocumentPointerDown, true);
  document.addEventListener("keydown", onDocumentKeydown, true);
});

onBeforeUnmount(() => {
  clearCloseTimer();
  document.removeEventListener("pointerdown", onDocumentPointerDown, true);
  document.removeEventListener("keydown", onDocumentKeydown, true);
});

watch(
  () => props.text,
  () => hide(),
);
</script>

<template>
  <span
    ref="root"
    class="relative inline-flex shrink-0"
    @mouseenter="show"
    @mouseleave="scheduleHide"
  >
    <button
      type="button"
      class="inline-flex h-10 w-10 items-center justify-center rounded-full text-surface-mid transition-colors hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      aria-label="help"
      :aria-expanded="open"
      :aria-controls="panelId"
      @click.stop="toggle"
      @focus="show"
      @blur="scheduleHide"
    >
      <QuestionIcon class-name="size-3.5" />
    </button>
    <span
      :id="panelId"
      role="tooltip"
      class="absolute top-full z-20 mt-1 w-max max-w-[min(100vw-2rem,18rem)] rounded-md border border-surface-border bg-surface-card px-2.5 py-1.5 text-xs lowercase leading-normal text-surface-mid shadow-lg"
      :class="[align === 'end' ? 'right-0' : 'left-0', open ? undefined : 'sr-only']"
    >
      {{ text }}
    </span>
  </span>
</template>
