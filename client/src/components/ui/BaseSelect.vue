<script setup lang="ts">
import { computed, useId } from "vue";

import { SELECT_CLASS, SELECT_CLASS_COMPACT } from "@/constants/formClasses";

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  label?: string;
  hint?: string;
  error?: string;
  compact?: boolean;
}>();

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
</script>

<template>
  <div class="flex flex-col gap-1">
    <label v-if="label" :for="selectId" class="text-label text-surface-sage">
      {{ label }}
    </label>
    <select
      :id="selectId"
      v-model="model"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="[selectClass, error && 'border-status-error']"
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
