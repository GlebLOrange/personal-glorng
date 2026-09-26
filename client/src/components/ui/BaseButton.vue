<script setup lang="ts">
import { computed } from "vue";

import {
  CONTROL_BUTTON_ICON,
  CONTROL_BUTTON_LG,
  CONTROL_BUTTON_MD,
  CONTROL_BUTTON_SM,
} from "@/constants/formClasses";
import {
  classesForActionButton,
  type BaseButtonVariant,
} from "@/constants/actionButtonVariants";

const props = withDefaults(
  defineProps<{
    /** Semantic actions (`create`, `add`, `save`, …) map to HTTP 1xx–5xx colors — see ui/README.md. */
    variant?: BaseButtonVariant;
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
    /** Persist selected/pressed chrome (solid primary ring, or grayscale wash). */
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

const variantClass = computed(() =>
  classesForActionButton({
    variant: props.variant ?? "secondary",
    selected: Boolean(props.selected),
    quiet: props.quiet,
    danger: props.danger,
  }),
);
</script>

<template>
  <button
    :type="type ?? 'button'"
    :disabled="isDisabled"
    :aria-busy="loading ? true : undefined"
    :aria-pressed="selected ? true : undefined"
    :class="[
      'inline-flex shrink-0 items-center justify-center whitespace-nowrap rounded-lg border font-medium leading-none transition-colors duration-200',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50',
      'disabled:cursor-not-allowed disabled:opacity-50',
      variantClass,
      sizeClass,
    ]"
  >
    <slot />
  </button>
</template>
