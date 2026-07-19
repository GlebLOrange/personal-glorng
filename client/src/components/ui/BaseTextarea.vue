<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import { TEXTAREA_CLASS } from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string>();

const props = defineProps<{
  id?: string;
  /** Faint tip drawn behind the value (full-width textarea). */
  placeholder?: string;
  /** Optional left-side field name inside the control. */
  prefix?: string;
  label?: string;
  hint?: string;
  error?: string;
  rows?: number;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const textareaId = computed(() => props.id ?? `base-textarea-${fallbackId}`);
const hintId = computed(() => `${textareaId.value}-hint`);
const errorId = computed(() => `${textareaId.value}-error`);
const tipId = computed(() => `${textareaId.value}-tip`);
const describedBy = computed(() => {
  const ids: string[] = [];
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  if (props.placeholder) ids.push(tipId.value);
  return ids.length ? ids.join(" ") : undefined;
});
const useShell = computed(() => Boolean(props.prefix || props.placeholder));
const bareClass = computed(() => [TEXTAREA_CLASS, props.error && "border-status-error"]);
const shellClass = computed(() => [
  "relative flex w-full items-start rounded-lg border bg-surface-dark transition-colors",
  props.error
    ? "border-status-error"
    : "border-surface-border focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50",
]);
const shellTextareaClass =
  "relative z-10 min-h-11 min-w-0 flex-1 resize-y border-0 bg-transparent px-3 py-2 text-left text-sm text-surface-light outline-none disabled:opacity-60";
const textareaAttrs = computed(() => {
  const nativeAttrs: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style") nativeAttrs[key] = value;
  }
  return nativeAttrs;
});
const accessibleName = computed(() => {
  if (typeof attrs["aria-label"] === "string" && attrs["aria-label"].trim()) {
    return attrs["aria-label"];
  }
  return props.label || props.prefix || props.placeholder || undefined;
});
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <label v-if="label && !useShell" :for="textareaId" class="text-label text-surface-sage">
      {{ label }}
    </label>

    <div v-if="useShell" :class="shellClass">
      <span
        v-if="prefix"
        class="relative z-10 shrink-0 pl-3 pt-2.5 text-xs font-medium uppercase tracking-wide text-surface-mid"
      >
        {{ prefix }}
      </span>
      <textarea
        :id="textareaId"
        v-bind="textareaAttrs"
        v-model="model"
        :rows="rows ?? 5"
        :aria-label="accessibleName"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="shellTextareaClass"
      />
      <span
        v-if="placeholder"
        :id="tipId"
        class="pointer-events-none absolute right-3 top-2.5 z-0 text-right text-xs text-surface-mid/40"
        aria-hidden="true"
      >
        {{ placeholder }}
      </span>
    </div>

    <textarea
      v-else
      :id="textareaId"
      v-bind="textareaAttrs"
      v-model="model"
      :rows="rows ?? 5"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="bareClass"
    />

    <p v-if="error" :id="errorId" role="alert" class="text-xs text-status-error">
      {{ error }}
    </p>
    <p v-else-if="hint" :id="hintId" class="text-xs text-surface-mid">
      {{ hint }}
    </p>
  </div>
</template>
