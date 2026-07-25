<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "ghost" | "success";
    /**
     * Shared control height with inputs (h-11), except lg (h-12).
     * sm/md/field share the same height; sm only tightens padding/type.
     * `field` is an alias of `md`.
     */
    size?: "sm" | "md" | "lg" | "field";
    /** Destructive action — red tint/text on hover. */
    danger?: boolean;
    /** Ghost only: muted text until hover / focus-visible. */
    quiet?: boolean;
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

const variantClass = computed(() => {
  if (props.variant === "success") {
    return "bg-status-success text-surface-dark hover:enabled:bg-status-success/90 active:enabled:bg-status-success/80 focus-visible:ring-status-success/50";
  }
  if (props.variant === "primary") {
    return "bg-accent-blue text-surface-dark hover:enabled:bg-accent-blue/90 active:enabled:bg-accent-blue/80";
  }
  if (props.variant === "ghost") {
    if (props.danger) {
      // ponytail: danger ghost is always quiet (muted until hover/focus)
      return "bg-transparent text-surface-light/60 hover:enabled:bg-status-error/10 hover:enabled:text-status-error active:enabled:bg-status-error/20 focus-visible:bg-status-error/10 focus-visible:text-status-error";
    }
    if (props.quiet) {
      return "bg-transparent text-surface-light/60 hover:enabled:bg-accent-blue/15 hover:enabled:text-accent-blue active:enabled:bg-accent-blue/25 focus-visible:bg-accent-blue/15 focus-visible:text-accent-blue";
    }
    return "bg-transparent text-surface-light hover:enabled:bg-accent-blue/15 hover:enabled:text-accent-blue active:enabled:bg-accent-blue/25";
  }
  // secondary
  if (props.danger) {
    return "bg-surface-card text-surface-light hover:enabled:bg-status-error/10 hover:enabled:text-status-error active:enabled:bg-status-error/20";
  }
  return "bg-surface-card text-surface-light hover:enabled:bg-accent-blue/15 hover:enabled:text-accent-blue active:enabled:bg-accent-blue/25";
});
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="isDisabled"
    :aria-busy="loading ? true : undefined"
    :class="[
      'inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg font-medium leading-none transition-all duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:cursor-not-allowed disabled:opacity-50',
      variantClass,
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
