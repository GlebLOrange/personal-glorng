<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "ghost" | "success";
    /**
     * Shared control height with inputs (h-11), except lg (h-12).
     * sm/md/field share the same height; sm only tightens padding/type.
     * `field` is an alias of `md`. `icon` is a square ≥44px hit target for glyph-only actions.
     */
    size?: "sm" | "md" | "lg" | "field" | "icon";
    /** Destructive action — red tint/text on hover. */
    danger?: boolean;
    /** Ghost only: muted text until hover / focus-visible. */
    quiet?: boolean;
    /** Persist hover styles (pale tint + accent text). */
    selected?: boolean;
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
  const selected = Boolean(props.selected);

  // Option C + fill/3 shadow wash; idle text matches fill accent. Hover/selected = /15 tint + accent border.
  if (props.variant === "success") {
    if (selected) {
      return "border-status-success/40 bg-status-success/15 text-status-success focus-visible:ring-status-success/50";
    }
    return "border-transparent bg-status-success/3 text-status-success hover:enabled:border-status-success/40 hover:enabled:bg-status-success/15 active:enabled:bg-status-success/25 focus-visible:ring-status-success/50";
  }

  if (props.danger) {
    // ponytail: danger ghost is always quiet (muted until hover/focus)
    if (selected) {
      return "border-status-error/40 bg-status-error/10 text-status-error";
    }
    if (props.variant === "ghost" || props.quiet) {
      return "border-transparent bg-transparent text-surface-light/60 hover:enabled:border-status-error/40 hover:enabled:bg-status-error/10 hover:enabled:text-status-error active:enabled:bg-status-error/20 focus-visible:border-status-error/40 focus-visible:bg-status-error/10 focus-visible:text-status-error";
    }
    return "border-transparent bg-status-error/3 text-status-error hover:enabled:border-status-error/40 hover:enabled:bg-status-error/10 active:enabled:bg-status-error/20";
  }

  if (props.variant === "ghost") {
    if (props.quiet && !selected) {
      return "border-transparent bg-transparent text-surface-light/60 hover:enabled:border-accent-blue/40 hover:enabled:bg-accent-blue/15 hover:enabled:text-accent-blue active:enabled:bg-accent-blue/25 focus-visible:border-accent-blue/40 focus-visible:bg-accent-blue/15 focus-visible:text-accent-blue";
    }
    if (selected) {
      return "border-accent-blue/40 bg-accent-blue/15 text-accent-blue";
    }
    return "border-transparent bg-accent-blue/3 text-accent-blue hover:enabled:border-accent-blue/40 hover:enabled:bg-accent-blue/15 active:enabled:bg-accent-blue/25";
  }

  if (props.variant === "primary") {
    if (selected) {
      return "border-accent-blue/40 bg-accent-blue/15 text-accent-blue";
    }
    return "border-transparent bg-accent-blue/3 text-accent-blue hover:enabled:border-accent-blue/40 hover:enabled:bg-accent-blue/15 active:enabled:bg-accent-blue/25";
  }

  // secondary — grayscale hierarchy (Toss); not accent wash
  if (selected) {
    return "border-surface-light/40 bg-surface-light/15 text-surface-light";
  }
  return "border-transparent bg-transparent text-surface-light/80 hover:enabled:border-surface-light/40 hover:enabled:bg-surface-light/10 hover:enabled:text-surface-light active:enabled:bg-surface-light/15";
});
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="isDisabled"
    :aria-busy="loading ? true : undefined"
    :aria-pressed="selected ? true : undefined"
    :class="[
      'inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg border font-medium leading-none transition-[color,background-color,border-color,opacity,box-shadow] duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:cursor-not-allowed disabled:opacity-50',
      variantClass,
      resolvedSize === 'lg'
        ? 'h-12 px-6 text-base'
        : resolvedSize === 'icon'
          ? 'h-11 w-11 min-h-11 min-w-11 px-0 text-xs'
          : resolvedSize === 'sm'
            ? 'h-11 px-3 text-xs'
            : 'h-11 px-4 text-sm',
    ]"
  >
    <slot />
  </button>
</template>
