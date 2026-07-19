<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useId } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { useScrollLock } from "@/composables/useScrollLock";
import { focusEditableField } from "@/utils/focusField";

const props = defineProps<{
  title?: string;
  maxWidth?: "md" | "lg" | "2xl";
  ariaLabel?: string;
}>();

const widthClass: Record<string, string> = {
  md: "max-w-md",
  lg: "max-w-lg",
  "2xl": "max-w-2xl",
};
const emit = defineEmits<{ close: [] }>();

const modalRef = ref<HTMLElement | null>(null);
const titleId = useId();
let previouslyFocusedElement: HTMLElement | null = null;
let focusRafId = 0;

useScrollLock(() => true);

function getFocusableElements(el: HTMLElement): HTMLElement[] {
  return Array.from(
    el.querySelectorAll<HTMLElement>(
      'a[href], area[href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), button:not([disabled]), iframe, object, embed, [tabindex="0"], [contenteditable]',
    ),
  ).filter((item) => item.tabIndex >= 0);
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") {
    emit("close");
    return;
  }

  if (e.key === "Tab") {
    if (!modalRef.value) return;
    const focusables = getFocusableElements(modalRef.value);
    if (focusables.length === 0) {
      e.preventDefault();
      return;
    }
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    const active = document.activeElement;

    if (e.shiftKey) {
      if (active === first || !modalRef.value.contains(active)) {
        last.focus();
        e.preventDefault();
      }
    } else {
      if (active === last || !modalRef.value.contains(active)) {
        first.focus();
        e.preventDefault();
      }
    }
  }
}

const labelledBy = computed(() => (props.title ? titleId : undefined));
const dialogLabel = computed(() => (props.title ? undefined : (props.ariaLabel ?? "Dialog")));

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  previouslyFocusedElement = document.activeElement as HTMLElement;

  focusRafId = requestAnimationFrame(() => {
    if (!modalRef.value) return;
    if (!modalRef.value.contains(document.activeElement)) {
      const focusables = getFocusableElements(modalRef.value);
      focusEditableField(modalRef.value, focusables[0] ?? modalRef.value);
    }
  });
});

onUnmounted(() => {
  cancelAnimationFrame(focusRafId);
  document.removeEventListener("keydown", onKeydown);
  if (previouslyFocusedElement) {
    previouslyFocusedElement.focus();
  }
});
</script>

<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-surface-dark/80 backdrop-blur-sm"
        aria-hidden="true"
        @click="$emit('close')"
      />
      <div
        ref="modalRef"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="labelledBy"
        :aria-label="dialogLabel"
        tabindex="-1"
        :class="[
          'relative flex max-h-[calc(100dvh-2rem)] w-full flex-col bg-surface-card border border-surface-border rounded-xl shadow-sm focus:outline-none',
          widthClass[maxWidth ?? 'lg'],
        ]"
      >
        <div class="flex shrink-0 items-center gap-2 px-6 pt-5 pb-3">
          <div class="min-w-0 flex-1">
            <slot name="header" :title-id="titleId">
              <h2 v-if="title" :id="titleId" class="text-lg font-bold text-surface-light">
                {{ title }}
              </h2>
            </slot>
          </div>
          <IconCloseButton
            class="w-[10%] shrink-0"
            aria-label="Close"
            @click="$emit('close')"
          />
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto overscroll-contain px-6 pb-8 [scrollbar-gutter:stable]">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>
