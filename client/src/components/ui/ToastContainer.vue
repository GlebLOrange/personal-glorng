<script setup lang="ts">
import { computed } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { Card } from "@/components/ui/card";
import { useNotify } from "@/composables/useNotify";
import type { Toast } from "@/types";

const { toasts, dismiss, pause, resume } = useNotify();

const hasToasts = computed(() => toasts.value.length > 0);

function toastCardClass(type: Toast["type"]): string {
  if (type === "success") return "border-status-success/40 bg-status-success/10";
  return "";
}

function toastTextClass(type: Toast["type"]): string {
  if (type === "error") return "text-status-error";
  if (type === "success") return "text-status-success";
  return "text-surface-light";
}
</script>

<template>
  <div
    v-if="hasToasts"
    class="pointer-events-none fixed inset-x-0 top-16 z-50 flex justify-center px-4 sm:justify-end sm:px-6"
    aria-label="Notifications"
  >
    <div class="pointer-events-auto flex w-full max-w-sm flex-col gap-2">
      <Card
        v-for="t in toasts"
        :key="t.id"
        :tint="t.type === 'error' ? 'danger' : 'default'"
        variant="dense"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        :class="['flex w-full items-center gap-2', toastCardClass(t.type)]"
        @mouseenter="pause(t.id)"
        @mouseleave="resume(t.id)"
        @focusin="pause(t.id)"
        @focusout="resume(t.id)"
      >
        <p
          class="min-w-0 flex-1 break-words text-center text-sm leading-snug"
          :class="toastTextClass(t.type)"
        >
          {{ t.message }}
        </p>
        <IconCloseButton aria-label="Dismiss notification" @click="dismiss(t.id)" />
      </Card>
    </div>
  </div>
</template>
