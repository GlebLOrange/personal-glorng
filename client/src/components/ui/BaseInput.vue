<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import { FIELD_INPUT_CLASS, FIELD_INPUT_CLASS_COMPACT } from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  type?: string;
  placeholder?: string;
  label?: string;
  compact?: boolean;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const inputId = computed(() => props.id ?? `base-input-${fallbackId}`);
const inputClass = computed(() => (props.compact ? FIELD_INPUT_CLASS_COMPACT : FIELD_INPUT_CLASS));
const inputAttrs = computed(() => {
  const nativeAttrs: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style") nativeAttrs[key] = value;
  }
  return nativeAttrs;
});
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <input
      v-if="type === 'number'"
      :id="inputId"
      v-bind="inputAttrs"
      v-model.number="model"
      type="number"
      :placeholder="placeholder"
      :class="[inputClass, 'font-data']"
    />
    <input
      v-else
      :id="inputId"
      v-bind="inputAttrs"
      v-model="model"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      :class="inputClass"
    />
  </div>
</template>
