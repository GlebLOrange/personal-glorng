<script setup lang="ts">
defineProps<{
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
}>();
</script>

<template>
  <button
    :disabled="disabled"
    :class="[
      'font-mono font-medium transition-all duration-200 rounded-lg border',
      'focus:outline-none focus:ring-2 focus:ring-accent-blue/50',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      variant === 'primary'
        ? 'bg-gradient-to-r from-accent-blue to-accent-violet text-white border-transparent hover:opacity-90'
        : variant === 'ghost'
          ? 'bg-transparent text-surface-light border-surface-border hover:border-accent-blue'
          : 'bg-surface-card text-surface-light border-surface-border hover:border-accent-blue',
      size === 'sm'
        ? 'px-3 py-1.5 text-xs'
        : size === 'lg'
          ? 'px-6 py-3 text-base'
          : 'px-4 py-2 text-sm',
    ]"
  >
    <slot />
  </button>
</template>
