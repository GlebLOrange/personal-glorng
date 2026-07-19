<script setup lang="ts">
import { useNotify } from "@/composables/useNotify";

import type { Toast } from "@/types";

const { toasts, dismiss, pause, resume } = useNotify();

const typeBorderClass: Record<Toast["type"], string> = {
  success: "border-status-success",
  error: "border-status-error",
  info: "",
};
</script>

<template>
  <div
    class="fixed top-4 right-4 z-[9999] flex max-w-[calc(100vw-2rem)] flex-col items-end gap-2 pt-[env(safe-area-inset-top)] pr-[env(safe-area-inset-right)]"
    aria-label="Notifications"
  >
    <div
      v-for="t in toasts"
      :key="t.id"
      :role="t.type === 'error' ? 'alert' : 'status'"
      :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
      :class="[
        'flex w-max max-w-full items-start gap-2 rounded-lg border bg-surface-card px-3 py-2 text-surface-light motion-safe:animate-[slide-in_0.3s_ease-out]',
        typeBorderClass[t.type] || 'border-surface-border',
      ]"
      @mouseenter="pause(t.id)"
      @mouseleave="resume(t.id)"
      @focusin="pause(t.id)"
      @focusout="resume(t.id)"
    >
      <p class="min-w-0 max-w-[18rem] flex-1 break-words text-sm leading-snug sm:max-w-[22rem]">
        {{ t.message }}
      </p>
      <button
        type="button"
        class="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-md text-base leading-none text-surface-mid hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
        aria-label="Dismiss notification"
        @click="dismiss(t.id)"
      >
        ×
      </button>
    </div>
  </div>
</template>

<style scoped>
@keyframes slide-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
