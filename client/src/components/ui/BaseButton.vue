<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "ghost";
    /**
     * Shared control height with inputs (h-11), except lg (h-12).
     * sm/md/field share the same height; sm only tightens padding/type.
     * `field` is an alias of `md`.
     */
    size?: "sm" | "md" | "lg" | "field";
    /** Destructive action — red border/text on hover. */
    danger?: boolean;
    disabled?: boolean;
    loading?: boolean;
    type?: "button" | "submit" | "reset";
  }>(),
  {
    size: "md",
  },
);

const isDisabled = computed(() => Boolean(props.disabled || props.loading));
const resolvedSize = computed(() => (props.size === "field" ? "md" : props.size));
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="isDisabled"
    :aria-busy="loading ? true : undefined"
    :class="[
      'inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg border font-medium leading-none transition-all duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:cursor-not-allowed disabled:opacity-50',
      'active:enabled:opacity-80',
      variant === 'primary'
        ? 'border-transparent bg-accent-blue text-surface-dark hover:enabled:bg-accent-blue/90'
        : variant === 'ghost'
          ? danger
            ? 'border-surface-border bg-transparent text-surface-light hover:enabled:border-status-error hover:enabled:bg-status-error/10 hover:enabled:text-status-error'
            : 'border-surface-border bg-transparent text-surface-light hover:enabled:border-accent-blue'
          : danger
            ? 'border-surface-border bg-surface-card text-surface-light hover:enabled:border-status-error hover:enabled:bg-status-error/10 hover:enabled:text-status-error'
            : 'border-surface-border bg-surface-card text-surface-light hover:enabled:border-accent-blue',
      resolvedSize === 'lg'
        ? 'h-12 px-6 text-base'
        : resolvedSize === 'sm'
          ? 'h-11 px-3 text-xs'
          : 'h-11 px-4 text-sm',
    ]"
  >
    <slot />
  </button>
</template>
