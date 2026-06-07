<script setup lang="ts">
import { onMounted, onUnmounted, ref, useTemplateRef } from "vue";

const open = ref(false);
const rootRef = useTemplateRef<HTMLElement>("root");

function toggle(): void {
  open.value = !open.value;
}

function close(): void {
  open.value = false;
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

function onItemSelect(): void {
  close();
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
    <button
      type="button"
      class="text-surface-mid hover:text-surface-light transition-colors p-1 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      aria-haspopup="menu"
      :aria-expanded="open"
      @click.stop="toggle"
    >
      <slot name="trigger">
        <span class="text-lg leading-none" aria-hidden="true">⋮</span>
      </slot>
    </button>

    <div
      v-if="open"
      role="menu"
      class="absolute right-0 top-full mt-1 z-10 bg-surface-card border border-surface-border rounded-lg shadow-lg py-1 min-w-[10rem]"
      @click.stop
    >
      <slot :close="onItemSelect" />
    </div>
  </div>
</template>
