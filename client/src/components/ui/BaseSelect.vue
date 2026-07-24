<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import { SELECT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  label?: string;
  hint?: string;
  error?: string;
  compact?: boolean;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const selectId = computed(() => props.id ?? `base-select-${fallbackId}`);
const hintId = computed(() => `${selectId.value}-hint`);
const errorId = computed(() => `${selectId.value}-error`);
const describedBy = computed(() => {
  const ids: string[] = [];
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  return ids.length ? ids.join(" ") : undefined;
});
const selectClass = computed(() => (props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS));
const ariaLabel = computed(() => {
  if (props.label) return undefined;
  const value = attrs["aria-label"];
  return typeof value === "string" ? value : undefined;
});
</script>

<template>
  <div class="flex flex-col gap-1" :class="attrs.class">
    <label v-if="label" :for="selectId" class="text-label text-surface-sage">
      {{ label }}
    </label>
    <select
      :id="selectId"
      v-model="model"
      :aria-label="ariaLabel"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="[selectClass, 'w-full', error && 'border-status-error']"
    >
      <slot />
    </select>
    <p v-if="error" :id="errorId" role="alert" class="text-xs text-status-error">
      {{ error }}
    </p>
    <p v-else-if="hint" :id="hintId" class="text-xs text-surface-mid">
      {{ hint }}
    </p>
  </div>
</template>
