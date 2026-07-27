<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { Card } from "@/components/ui/card";
import { useNotify } from "@/composables/useNotify";
import type { Toast } from "@/types";

const props = withDefaults(
  defineProps<{
    variant?: "tile" | "overlay";
  }>(),
  {
    variant: "overlay",
  },
);

const { toasts, tileHostClaimed, dismiss, pause, resume, claimTileHost, releaseTileHost } =
  useNotify();

/* ponytail: ! beats Card default bg/border; ceiling = no twMerge — fix Card class merge instead. */
const TOAST_SURFACE: Record<Toast["type"], string> = {
  success: "text-status-success !bg-status-success/10 !border-status-success/30",
  error: "text-status-error !bg-status-error/10 !border-status-error/30",
  info: "text-accent-blue !bg-accent-blue/10 !border-accent-blue/30",
};

const TOAST_HOVER: Record<Toast["type"], string> = {
  success: "hover:!bg-status-success/20 hover:!border-status-success/50",
  error: "hover:!bg-status-error/20 hover:!border-status-error/50",
  info: "hover:!bg-accent-blue/20 hover:!border-accent-blue/50",
};

const TOAST_TEXT: Record<Toast["type"], string> = {
  success: "text-status-success",
  error: "text-status-error",
  info: "text-accent-blue",
};

const hasToasts = computed(() => toasts.value.length > 0);

/** Worst type in the queue drives the stack surface (error > success > info). */
const stackSurfaceType = computed((): Toast["type"] => {
  const types = toasts.value.map((t) => t.type);
  if (types.includes("error")) return "error";
  if (types.includes("success")) return "success";
  return "info";
});

/**
 * Tile slot matches the weather bar height — do not stack every toast or the grid jumps.
 * Overlay keeps the full queue.
 */
const visibleToasts = computed(() => {
  if (props.variant !== "tile") return toasts.value;
  const last = toasts.value[toasts.value.length - 1];
  return last ? [last] : [];
});

const shouldRender = computed(() => {
  if (!hasToasts.value) return false;
  if (props.variant === "tile") return true;
  return !tileHostClaimed.value;
});

onMounted(() => {
  if (props.variant === "tile") claimTileHost();
});

onUnmounted(() => {
  if (props.variant === "tile") releaseTileHost();
});
</script>

<template>
  <div
    v-if="shouldRender"
    data-testid="toast-host"
    aria-label="notifications"
    :class="
      variant === 'tile'
        ? 'page-tile md:col-start-2 min-w-0 md:h-0 md:min-h-full md:overflow-hidden'
        : 'pointer-events-none fixed inset-x-0 top-[5.5rem] z-50 flex justify-center px-4 sm:justify-end sm:px-6'
    "
  >
    <Card
      v-if="variant === 'tile'"
      class="page-weather-tile-card h-full max-h-full w-full gap-2 md:overflow-y-auto md:overscroll-contain transition-colors duration-200"
      :class="[TOAST_SURFACE[stackSurfaceType], TOAST_HOVER[stackSurfaceType]]"
    >
      <div
        v-for="t in visibleToasts"
        :key="t.id"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        :class="['flex w-full max-w-full items-center justify-center gap-2', TOAST_TEXT[t.type]]"
        @mouseenter="pause(t.id)"
        @mouseleave="resume(t.id)"
        @focusin="pause(t.id)"
        @focusout="resume(t.id)"
      >
        <p class="min-w-0 flex-1 break-words text-center text-base lowercase leading-snug">
          {{ t.message }}
        </p>
        <IconCloseButton aria-label="dismiss notification" @click="dismiss(t.id)" />
      </div>
    </Card>

    <div
      v-else
      class="pointer-events-auto flex w-full max-w-sm flex-col gap-2"
      :class="[TOAST_SURFACE[stackSurfaceType], TOAST_HOVER[stackSurfaceType]]"
    >
      <Card
        v-for="t in visibleToasts"
        :key="t.id"
        :tint="t.type === 'error' ? 'danger' : 'default'"
        variant="dense"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        :class="['flex w-full items-center gap-2', TOAST_TEXT[t.type]]"
        @mouseenter="pause(t.id)"
        @mouseleave="resume(t.id)"
        @focusin="pause(t.id)"
        @focusout="resume(t.id)"
      >
        <p class="min-w-0 flex-1 break-words text-center text-base lowercase leading-snug">
          {{ t.message }}
        </p>
        <IconCloseButton aria-label="dismiss notification" @click="dismiss(t.id)" />
      </Card>
    </div>
  </div>
</template>
