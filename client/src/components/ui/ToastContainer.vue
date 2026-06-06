<script setup lang="ts">
import { useNotify } from "@/composables/useNotify";

import type { Toast } from "@/types";

const { toasts, dismiss } = useNotify();

const typeBorderClass: Record<Toast["type"], string> = {
  success: "border-green-500",
  error: "border-accent-violet",
  info: "",
};
</script>

<template>
  <div class="fixed top-4 right-4 z-[9999] flex flex-col gap-2">
    <div
      v-for="t in toasts"
      :key="t.id"
      :class="[
        'bg-surface-card border rounded-lg p-4 text-surface-light min-w-[280px] cursor-pointer animate-[slide-in_0.3s_ease-out]',
        typeBorderClass[t.type] || 'border-surface-border',
      ]"
      @click="dismiss(t.id)"
    >
      {{ t.message }}
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
