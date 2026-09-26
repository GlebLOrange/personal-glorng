<script setup lang="ts">
import { computed, useAttrs } from "vue";

import {
  httpFamilyForSemanticAction,
  type SemanticButtonAction,
} from "@/constants/actionButtonVariants";
import { actionFamilyClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

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
const resolvedFamily = computed((): HttpStatusFamily =>
  props.action ? httpFamilyForSemanticAction(props.action) : props.family,
);

const classes = computed(() => [
  actionFamilyClass(resolvedFamily.value, props.selected),
  attrs.class,
]);
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
