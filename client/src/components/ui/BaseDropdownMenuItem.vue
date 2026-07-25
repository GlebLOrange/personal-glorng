<script setup lang="ts">
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
      'w-[calc(100%-0.5rem)] text-left px-3 py-2 text-sm transition-colors border border-transparent rounded-md mx-1 my-0.5',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      colorClass
        ? [colorClass, 'hover:border-current/35 focus-visible:border-current/35']
        : destructive
          ? 'text-status-error hover:bg-status-error/10 hover:border-status-error/40 focus-visible:border-status-error/40'
          : 'text-surface-light hover:bg-surface-border/40 hover:border-surface-border focus-visible:border-surface-border',
    ]"
    @click="onClick"
  >
    <slot />
  </button>
</template>
