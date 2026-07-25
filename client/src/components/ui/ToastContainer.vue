<script setup lang="ts">
import { computed } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { Card } from "@/components/ui/card";
import { useNotify } from "@/composables/useNotify";

import type { Toast } from "@/types";

const { toasts, dismiss, pause, resume } = useNotify();

const hasToasts = computed(() => toasts.value.length > 0);

const typeBorderClass: Record<Toast["type"], string> = {
  success: "border-status-success",
  error: "border-status-error",
  info: "border-surface-border",
};
</script>

<template>
  <div
    v-if="hasToasts"
    class="page-tile md:col-start-2"
    aria-label="Notifications"
  >
    <Card class="page-weather-tile-card h-full gap-2">
      <div
        v-for="t in toasts"
        :key="t.id"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        :class="[
          'flex w-full max-w-full items-start gap-2 rounded-lg border bg-surface-card/80 px-3 py-2 text-surface-light',
          typeBorderClass[t.type],
        ]"
        @mouseenter="pause(t.id)"
        @mouseleave="resume(t.id)"
        @focusin="pause(t.id)"
        @focusout="resume(t.id)"
      >
        <p class="min-w-0 flex-1 break-words text-center text-sm leading-snug">
          {{ t.message }}
        </p>
        <IconCloseButton
          aria-label="Dismiss notification"
          @click="dismiss(t.id)"
        />
      </div>
    </Card>
  </div>
</template>
