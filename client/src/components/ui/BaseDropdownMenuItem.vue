<script setup lang="ts">
import ChevronIcon from "@/components/icons/ChevronIcon.vue";

defineProps<{
  destructive?: boolean;
  /** Optional text + hover classes (overrides default / destructive styling). */
  colorClass?: string;
}>();

const emit = defineEmits<{
  select: [];
}>();

function onClick(): void {
  emit("select");
}
</script>

<template>
  <button
    type="button"
    role="menuitem"
    :class="[
      'mx-1 my-0.5 flex w-[calc(100%-0.5rem)] items-center gap-1.5 rounded-md border border-transparent px-3 py-2 text-left text-sm transition-colors',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50',
      colorClass
        ? [colorClass, 'hover:border-current/35 focus-visible:border-current/35']
        : destructive
          ? 'text-status-error hover:bg-status-error/15 hover:border-status-error/40 focus-visible:border-status-error/40'
          : 'text-surface-light hover:bg-surface-border/40 hover:border-surface-border focus-visible:border-surface-border',
    ]"
    @click="onClick"
  >
    <ChevronIcon direction="right" class-name="size-3.5 shrink-0 opacity-70" />
    <slot />
  </button>
</template>
