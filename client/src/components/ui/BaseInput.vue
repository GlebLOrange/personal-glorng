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
  hint?: string;
  error?: string;
  compact?: boolean;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const inputId = computed(() => props.id ?? `base-input-${fallbackId}`);
const hintId = computed(() => `${inputId.value}-hint`);
const errorId = computed(() => `${inputId.value}-error`);
const describedBy = computed(() => {
  const ids: string[] = [];
  const fromAttrs = attrs["aria-describedby"];
  if (typeof fromAttrs === "string" && fromAttrs.trim()) {
    ids.push(...fromAttrs.trim().split(/\s+/));
  }
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  return ids.length ? [...new Set(ids)].join(" ") : undefined;
});
const inputClass = computed(() => (props.compact ? FIELD_INPUT_CLASS_COMPACT : FIELD_INPUT_CLASS));
const inputAttrs = computed(() => {
  const nativeAttrs: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style" && key !== "aria-describedby") nativeAttrs[key] = value;
  }
  return nativeAttrs;
});
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <label v-if="label" :for="inputId" class="text-label text-surface-sage">
      {{ label }}
    </label>
    <input
      v-if="type === 'number'"
      :id="inputId"
      v-bind="inputAttrs"
      v-model.number="model"
      type="number"
      :placeholder="placeholder"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="[inputClass, 'font-data', error && 'border-status-error']"
    />
    <input
      v-else
      :id="inputId"
      v-bind="inputAttrs"
      v-model="model"
      :type="type ?? 'text'"
      :placeholder="placeholder"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="[inputClass, error && 'border-status-error']"
    />
    <p v-if="error" :id="errorId" role="alert" class="text-xs text-status-error">
      {{ error }}
    </p>
    <p v-else-if="hint" :id="hintId" class="text-xs text-surface-mid">
      {{ hint }}
    </p>
  </div>
</template>
