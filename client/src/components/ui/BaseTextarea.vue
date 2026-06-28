<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

defineOptions({ inheritAttrs: false });

const model = defineModel<string>();

const props = defineProps<{
  id?: string;
  placeholder?: string;
  label?: string;
  rows?: number;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const textareaId = computed(() => props.id ?? `base-textarea-${fallbackId}`);
const textareaAttrs = computed(() => {
  const nativeAttrs: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style") nativeAttrs[key] = value;
  }
  return nativeAttrs;
});
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <label v-if="label" :for="textareaId" class="text-sm text-surface-mid">{{ label }}</label>
    <textarea
      :id="textareaId"
      v-bind="textareaAttrs"
      v-model="model"
      :rows="rows ?? 5"
      :placeholder="placeholder"
      class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors placeholder:text-surface-mid/50 resize-y disabled:opacity-60"
    />
  </div>
</template>
