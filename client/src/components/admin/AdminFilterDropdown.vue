<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";

defineProps<{
  hasActiveFilters?: boolean;
  activeLabel?: string;
}>();

const emit = defineEmits<{
  clear: [];
}>();

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");

function toggle(): void {
  open.value = !open.value;
}

function close(): void {
  open.value = false;
}

function onClear(): void {
  emit("clear");
  close();
}

function onDocumentClick(event: MouseEvent): void {
  if (!open.value) return;
  const root = rootRef.value;
  if (root && !root.contains(event.target as Node)) {
    close();
  }
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && open.value) {
    event.stopPropagation();
    close();
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKeydown);
});

defineExpose({ close });
</script>

<template>
  <div ref="root" class="relative inline-flex">
    <BaseButton
      type="button"
      variant="ghost"
      size="sm"
      aria-haspopup="dialog"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      filters<span v-if="activeLabel" class="text-surface-muted"> · {{ activeLabel }}</span>
    </BaseButton>

    <div
      v-if="open"
      role="dialog"
      aria-label="filters"
      class="absolute left-0 top-full z-10 mt-1 w-[18rem] rounded-lg border border-surface-border bg-surface-card p-3 shadow-lg"
      @click.stop
    >
      <div class="space-y-3">
        <div v-if="$slots.chips" class="grid grid-cols-3 gap-2">
          <slot name="chips" />
        </div>
        <slot />
      </div>
      <slot name="footer" />
      <div v-if="hasActiveFilters" class="mt-3 flex flex-wrap justify-center gap-2">
        <BaseButton variant="ghost" size="sm" @click="onClear">clear</BaseButton>
      </div>
    </div>
  </div>
</template>
