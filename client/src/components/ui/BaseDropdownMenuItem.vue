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
      'w-full text-left px-3 py-2 text-sm transition-colors',
      colorClass
        ? colorClass
        : destructive
          ? 'text-status-error hover:bg-status-error/10'
          : 'text-surface-light hover:bg-surface-border/40',
    ]"
    @click="onClick"
  >
    <slot />
  </button>
</template>
