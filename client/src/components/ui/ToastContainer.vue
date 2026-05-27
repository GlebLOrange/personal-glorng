<script setup lang="ts">
import { useNotify } from "@/composables/useNotify";

const { toasts, dismiss } = useNotify();
</script>

<template>
  <div class="toast-container">
    <div
      v-for="t in toasts"
      :key="t.id"
      :class="['toast', t.type]"
      @click="dismiss(t.id)"
    >
      {{ t.message }}
    </div>
  </div>
</template>

<style scoped lang="scss">
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toast {
  font-family: "Roboto Mono", monospace;
  background: theme("colors.surface.card");
  border: 1px solid theme("colors.surface.border");
  border-radius: 0.5rem;
  padding: 1rem;
  color: theme("colors.surface.light");
  min-width: 280px;
  animation: slide-in 0.3s ease-out;
  cursor: pointer;

  &.success {
    border-color: #22c55e;
  }
  &.error {
    border-color: theme("colors.accent.violet");
  }
}

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
