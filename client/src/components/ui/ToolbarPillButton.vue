<script setup lang="ts">
import { computed, useAttrs } from "vue";

import {
  classesForActionButton,
  type SemanticButtonAction,
} from "@/constants/actionButtonVariants";
import { ACTION_PILL_BASE, actionFamilyClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    /** Prefer over raw `family` — same standard as BaseButton semantic variants. */
    action?: SemanticButtonAction;
    family?: HttpStatusFamily;
    selected?: boolean;
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
  }>(),
  {
    family: "1xx",
    selected: false,
    type: "button",
    disabled: false,
  },
);

defineEmits<{ click: [MouseEvent] }>();

const attrs = useAttrs();

/** Shape without hardcoded ring — classesForActionButton supplies focus ring. */
const PILL_SHAPE = ACTION_PILL_BASE.replace(" focus-visible:ring-accent-coral/50", "");

const classes = computed(() => {
  if (props.action) {
    return [
      PILL_SHAPE,
      classesForActionButton({ variant: props.action, selected: props.selected }),
      attrs.class,
    ];
  }
  return [actionFamilyClass(props.family, props.selected), attrs.class];
});
const nativeAttrs = computed(() => {
  const next: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style") next[key] = value;
  }
  return next;
});

const styleAttr = computed(() => attrs.style);
</script>

<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="classes"
    :style="styleAttr"
    v-bind="nativeAttrs"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>
