<script setup lang="ts">
defineProps<{
  label: string;
  active?: boolean;
  colorClass?: string;
}>();
</script>

<template>
  <button
    type="button"
    :aria-pressed="active"
    :class="[
      'w-full min-w-0 truncate text-center text-xs px-2 py-1 rounded-full border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      active
        ? 'ring-2 ring-accent-blue/50 border-accent-blue/40'
        : 'border-surface-border hover:border-accent-blue/40',
      colorClass,
    ]"
  >
    {{ label }}
  </button>
</template>
