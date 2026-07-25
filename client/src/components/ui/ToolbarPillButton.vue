<script setup lang="ts">
import { computed, useAttrs } from "vue";

import { actionFamilyClass, type HttpStatusFamily } from "@/constants/httpStatusColors";

defineOptions({ inheritAttrs: false });

const props = withDefaults(
  defineProps<{
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
const classes = computed(() => [actionFamilyClass(props.family, props.selected), attrs.class]);
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
