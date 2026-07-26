<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
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
  <div class="flex min-w-0 flex-col gap-1" :class="attrs.class">
    <div v-if="label || hint" class="flex items-center gap-1.5">
      <!-- associated via :for / :id (computed ids); FieldHelp sits beside the label -->
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label v-if="label" :for="selectId" class="text-label text-surface-sage">
        {{ label }}
      </label>
      <FieldHelp v-if="hint" :text="hint" :content-id="hintId" />
    </div>
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
  </div>
</template>
