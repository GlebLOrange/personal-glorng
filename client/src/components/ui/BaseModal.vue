<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";

defineProps<{ title?: string; maxWidth?: "md" | "lg" | "2xl" }>();

const widthClass: Record<string, string> = {
  md: "max-w-md",
  lg: "max-w-lg",
  "2xl": "max-w-2xl",
};
const emit = defineEmits<{ close: [] }>();

function onKeydown(e: KeyboardEvent) {
  if (e.key === "Escape") emit("close");
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
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
        :class="[
          'relative w-full bg-surface-card border border-surface-border rounded-xl shadow-2xl',
          widthClass[maxWidth ?? 'lg'],
        ]"
      >
        <div class="flex items-center justify-between px-6 pt-5 pb-3">
          <h2 v-if="title" class="text-lg font-bold text-surface-light">
            {{ title }}
          </h2>
          <button
            class="ml-auto text-surface-mid hover:text-surface-light transition-colors text-xl leading-none"
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
