<script setup lang="ts">
import { computed, useAttrs, type Component } from "vue";

import { ACTION_BUTTON_ICON } from "@/constants/actionButtonIcons";
import {
  classesForActionButton,
  type SemanticButtonAction,
} from "@/constants/actionButtonVariants";
import {
  ACTION_PILL_BASE,
  actionFamilyClass,
  type HttpStatusFamily,
} from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
    /** Prefer over raw `family` — same standard as BaseButton semantic variants. */
    action?: SemanticButtonAction;
    family?: HttpStatusFamily;
    selected?: boolean;
    type?: "button" | "submit" | "reset";
    disabled?: boolean;
    /**
     * Leading action SVG when `action` is set. Default true for mapped actions.
     * Set false when the slot already supplies the icon.
     * Vue boolean props default to false when omitted — keep this explicit true.
     */
    icon?: boolean;
  }>(),
  {
    family: "1xx",
    selected: false,
    type: "button",
    disabled: false,
    icon: true,
  },
);

defineEmits<{ click: [MouseEvent] }>();

const attrs = useAttrs();

/** Shape without hardcoded ring — classesForActionButton supplies focus ring. */
const PILL_SHAPE = ACTION_PILL_BASE.replace(" focus-visible:ring-accent-coral/50", "");

const mappedIcon = computed((): Component | undefined => {
  if (!props.action) return undefined;
  return ACTION_BUTTON_ICON[props.action];
});

const showLeadingIcon = computed(() => {
  if (props.icon === false) return false;
  if (props.icon === true) return Boolean(mappedIcon.value);
  return Boolean(mappedIcon.value);
});

const classes = computed(() => {
  if (props.action) {
    return [
      PILL_SHAPE,
      "inline-flex items-center justify-center gap-1.5",
      classesForActionButton({ variant: props.action, selected: props.selected }),
      attrs.class,
    ];
  }
  return [
    "inline-flex items-center justify-center gap-1.5",
    actionFamilyClass(props.family, props.selected),
    attrs.class,
  ];
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
    <component :is="mappedIcon" v-if="showLeadingIcon" class-name="size-3.5 shrink-0" />
    <slot />
  </button>
</template>
