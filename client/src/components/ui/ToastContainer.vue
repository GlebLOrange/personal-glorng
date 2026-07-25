<script setup lang="ts">
import { computed } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { Card } from "@/components/ui/card";
import { useNotify } from "@/composables/useNotify";
import type { Toast } from "@/types";

const { toasts, dismiss, pause, resume } = useNotify();

/* ponytail: ! beats Card default bg/border; ceiling = no twMerge — fix Card class merge instead. */
const TOAST_SURFACE: Record<Toast["type"], string> = {
  success: "text-status-success !bg-status-success/10 !border-status-success/30",
  error: "text-status-error !bg-status-error/10 !border-status-error/30",
  info: "text-accent-blue !bg-accent-blue/10 !border-accent-blue/30",
};

const TOAST_TEXT: Record<Toast["type"], string> = {
  success: "text-status-success",
  error: "text-status-error",
  info: "text-accent-blue",
};

const hasToasts = computed(() => toasts.value.length > 0);

/** Card chrome: error > success > first toast type. */
const cardSurfaceClass = computed(() => {
  const list = toasts.value;
  if (!list.length) return TOAST_SURFACE.info;
  if (list.some((t) => t.type === "error")) return TOAST_SURFACE.error;
  if (list.some((t) => t.type === "success")) return TOAST_SURFACE.success;
  return TOAST_SURFACE[list[0].type];
});
</script>

<template>
  <div
    v-if="hasToasts"
    class="page-tile md:col-start-2"
    aria-label="Notifications"
  >
    <Card :class="['page-weather-tile-card h-full w-full gap-3', cardSurfaceClass]">
      <div
        v-for="t in toasts"
        :key="t.id"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        :class="['flex w-full max-w-full items-center justify-center gap-2', TOAST_TEXT[t.type]]"
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
