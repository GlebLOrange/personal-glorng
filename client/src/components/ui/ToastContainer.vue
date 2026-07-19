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
    class="fixed top-4 right-4 z-[9999] flex flex-col gap-2 pt-[env(safe-area-inset-top)] pr-[env(safe-area-inset-right)]"
    aria-label="Notifications"
  >
    <div
      v-for="t in toasts"
      :key="t.id"
      :role="t.type === 'error' ? 'alert' : 'status'"
      :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
      :class="[
        'flex items-start gap-2 bg-surface-card border rounded-lg p-4 text-surface-light min-w-[280px] motion-safe:animate-[slide-in_0.3s_ease-out]',
        typeBorderClass[t.type] || 'border-surface-border',
      ]"
      @mouseenter="pause(t.id)"
      @mouseleave="resume(t.id)"
      @focusin="pause(t.id)"
      @focusout="resume(t.id)"
    >
      <p class="min-w-0 flex-1 text-sm">{{ t.message }}</p>
      <button
        type="button"
        class="inline-flex min-h-11 min-w-11 shrink-0 items-center justify-center rounded-lg text-surface-mid hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
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
