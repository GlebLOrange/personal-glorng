<script setup lang="ts">
import { computed, useAttrs } from "vue";

import {
  SEMANTIC_ACTION_HTTP_FAMILY,
  type SemanticButtonAction,
} from "@/constants/actionButtonVariants";
import { iconActionClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    /** Prefer over raw `family` — same standard as ToolbarPillButton. */
    action?: SemanticButtonAction;
    family?: HttpStatusFamily;
    /** Forces 4xx (delete / clear / close). */
    danger?: boolean;
    /** Muted until hover — then 1xx. */
    quiet?: boolean;
    /** Idle bg transparent; hover/focus add family wash. */
    transparentIdle?: boolean;
    selected?: boolean;
    disabled?: boolean;
    type?: "button" | "submit" | "reset";
    /** Accessible name for icon-only chrome (can also pass aria-label directly). */
    ariaLabel?: string;
    /** Opt-in native tooltip — omitted by default (aria-label covers a11y). */
    title?: string;
    /** field = in-shell clear (same h-10 square); default matches CONTROL_SIZE (h-10). */
    size?: "md" | "field";
  }>(),
  {
    family: "1xx",
    danger: false,
    quiet: false,
    transparentIdle: false,
    selected: false,
    disabled: false,
    type: "button",
    size: "md",
  },
);

defineEmits<{ click: [MouseEvent] }>();

const attrs = useAttrs();

const accessibleName = computed(
  () => props.ariaLabel ?? (attrs["aria-label"] as string | undefined) ?? props.title,
);

const resolvedFamily = computed((): HttpStatusFamily =>
  props.action ? SEMANTIC_ACTION_HTTP_FAMILY[props.action] : props.family,
);

const classes = computed(() =>
  [
    iconActionClass(resolvedFamily.value, props.selected, {
      danger: props.danger,
      quiet: props.quiet,
      transparentIdle: props.transparentIdle,
      size: props.size,
    }),
    attrs.class,
  ]
    .filter(Boolean)
    .join(" "),
);

const nativeAttrs = computed(() => {
  const next: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style" && key !== "aria-label") next[key] = value;
  }
  return next;
});
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    :aria-label="accessibleName"
    :aria-pressed="selected ? true : undefined"
    :title="title || undefined"
    :class="classes"
    :style="attrs.style"
    v-bind="nativeAttrs"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>
