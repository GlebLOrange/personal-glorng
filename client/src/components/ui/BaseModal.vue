<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useId } from "vue";

import { useScrollLock } from "@/composables/useScrollLock";

const props = defineProps<{ title?: string; maxWidth?: "md" | "lg" | "2xl" }>();

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

onMounted(() => {
  document.addEventListener("keydown", onKeydown);
  previouslyFocusedElement = document.activeElement as HTMLElement;

  focusRafId = requestAnimationFrame(() => {
    if (!modalRef.value) return;
    if (!modalRef.value.contains(document.activeElement)) {
      const focusables = getFocusableElements(modalRef.value);
      if (focusables.length > 0) {
        focusables[0].focus();
      } else {
        modalRef.value.focus();
      }
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
        tabindex="-1"
        :class="[
          'relative w-full bg-surface-card border border-surface-border rounded-xl shadow-sm focus:outline-none',
          widthClass[maxWidth ?? 'lg'],
        ]"
      >
        <div class="flex items-center justify-between px-6 pt-5 pb-3">
          <h2 v-if="title" :id="titleId" class="text-lg font-bold text-surface-light">
            {{ title }}
          </h2>
          <button
            type="button"
            class="ml-auto min-h-11 min-w-11 rounded text-xl leading-none text-surface-mid transition-colors hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
            aria-label="Close"
            @click="$emit('close')"
          >
            ×
          </button>
        </div>
        <div class="px-6 pb-6">
          <slot />
        </div>
      </div>
    </div>
  </Teleport>
</template>
