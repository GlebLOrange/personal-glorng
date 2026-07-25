<script setup lang="ts">
import { computed } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { Card } from "@/components/ui/card";
import { useNotify } from "@/composables/useNotify";

const { toasts, dismiss, pause, resume } = useNotify();

const hasToasts = computed(() => toasts.value.length > 0);
</script>

<template>
  <div
    v-if="hasToasts"
    class="page-tile md:col-start-2"
    aria-label="Notifications"
  >
    <Card class="page-weather-tile-card h-full w-full gap-3">
      <div
        v-for="t in toasts"
        :key="t.id"
        :role="t.type === 'error' ? 'alert' : 'status'"
        :aria-live="t.type === 'error' ? 'assertive' : 'polite'"
        class="flex w-full max-w-full items-center justify-center gap-2 text-surface-light"
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
