<script setup lang="ts">
import { computed } from "vue";

import {
  CONTROL_BUTTON_ICON,
  CONTROL_BUTTON_LG,
  CONTROL_BUTTON_MD,
  CONTROL_BUTTON_SM,
} from "@/constants/formClasses";
import { familyToneClass } from "@/constants/httpStatusColors";

const props = withDefaults(
  defineProps<{
    variant?: "primary" | "secondary" | "ghost" | "success";
    /**
     * Shared control height with inputs (h-10), except lg (h-12).
     * sm/md/field share the same height; sm only tightens padding/type.
     * `field` is an alias of `md`. `icon` is a square hit target matching field height.
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

const sizeClass = computed(() => {
  if (resolvedSize.value === "lg") return CONTROL_BUTTON_LG;
  if (resolvedSize.value === "icon") return CONTROL_BUTTON_ICON;
  if (resolvedSize.value === "sm") return CONTROL_BUTTON_SM;
  return CONTROL_BUTTON_MD;
});

const variantClass = computed(() => {
  const selected = Boolean(props.selected);

  if (props.variant === "success") {
    return `${familyToneClass("2xx", selected, { includeActive: true })} focus-visible:ring-status-success/50`;
  }

  if (props.danger) {
    // ponytail: danger ghost is always quiet (muted until hover/focus); wash matches pill 4xx (/15)
    if (props.variant === "ghost" || props.quiet) {
      return familyToneClass("4xx", selected, {
        quiet: true,
        includeFocusTint: true,
      });
    }
    return familyToneClass("4xx", selected, { includeActive: true });
  }

  if (props.variant === "ghost") {
    if (props.quiet && !selected) {
      return familyToneClass("1xx", false, {
        quiet: true,
        includeFocusTint: true,
      });
    }
    return familyToneClass("1xx", selected, { includeActive: true });
  }

  if (props.variant === "primary") {
    return familyToneClass("1xx", selected, { includeActive: true });
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
      'inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg border font-medium leading-none transition-all duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:cursor-not-allowed disabled:opacity-50',
      variantClass,
      sizeClass,
    ]"
  >
    <slot />
  </button>
</template>
