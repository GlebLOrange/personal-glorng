<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  variant?: "primary" | "secondary" | "ghost";
  size?: "sm" | "md" | "lg";
  disabled?: boolean;
  loading?: boolean;
  type?: "button" | "submit" | "reset";
}>();

const isDisabled = computed(() => Boolean(props.disabled || props.loading));
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="isDisabled"
    :aria-busy="loading ? true : undefined"
    :class="[
      'inline-flex items-center justify-center font-medium transition-all duration-200 rounded-lg border',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:opacity-50 disabled:cursor-not-allowed',
      'active:enabled:opacity-80',
      variant === 'primary'
        ? 'bg-accent-blue text-surface-dark border-transparent hover:enabled:bg-accent-blue/90'
        : variant === 'ghost'
          ? 'bg-transparent text-surface-light border-surface-border hover:enabled:border-accent-blue'
          : 'bg-surface-card text-surface-light border-surface-border hover:enabled:border-accent-blue',
      size === 'sm'
        ? 'min-h-9 px-3 py-1.5 text-xs'
        : size === 'lg'
          ? 'min-h-11 px-6 py-3 text-base'
          : 'min-h-11 px-4 py-2 text-sm',
    ]"
  >
    <slot />
  </button>
</template>
