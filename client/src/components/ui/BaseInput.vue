<script setup lang="ts">
import { computed, ref, useAttrs, useId } from "vue";

import { FIELD_INPUT_CLASS, FIELD_INPUT_CLASS_COMPACT } from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  type?: string;
  /** Faint right-aligned tip drawn behind the value (full-width input). */
  placeholder?: string;
  /** Optional left-side field name inside the control. */
  prefix?: string;
  label?: string;
  hint?: string;
  error?: string;
  compact?: boolean;
}>();

const attrs = useAttrs();
const inputEl = ref<HTMLInputElement | null>(null);
const fallbackId = useId();
const inputId = computed(() => props.id ?? `base-input-${fallbackId}`);
const hintId = computed(() => `${inputId.value}-hint`);
const errorId = computed(() => `${inputId.value}-error`);
const tipId = computed(() => `${inputId.value}-tip`);
const describedBy = computed(() => {
  const ids: string[] = [];
  const fromAttrs = attrs["aria-describedby"];
  if (typeof fromAttrs === "string" && fromAttrs.trim()) {
    ids.push(...fromAttrs.trim().split(/\s+/));
  }
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  if (props.placeholder) ids.push(tipId.value);
  return ids.length ? [...new Set(ids)].join(" ") : undefined;
});
const useShell = computed(() => Boolean(props.prefix || props.placeholder));
const bareInputClass = computed(() => [
  props.compact ? FIELD_INPUT_CLASS_COMPACT : FIELD_INPUT_CLASS,
  props.type === "number" && "font-data",
  props.error && "border-status-error",
]);
const shellClass = computed(() => [
  "relative flex w-full items-center rounded-lg border bg-surface-dark transition-colors",
  props.compact ? "h-9" : "h-11",
  props.error
    ? "border-status-error"
    : "border-surface-border focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50",
]);
const shellInputClass = computed(() => [
  "relative z-10 h-full min-w-0 flex-1 border-0 bg-transparent px-3 text-left text-sm text-surface-light outline-none",
  props.type === "number" && "font-data",
]);
const inputAttrs = computed(() => {
  const nativeAttrs: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(attrs)) {
    if (key !== "class" && key !== "style" && key !== "aria-describedby") nativeAttrs[key] = value;
  }
  return nativeAttrs;
});
const accessibleName = computed(() => {
  if (typeof attrs["aria-label"] === "string" && attrs["aria-label"].trim()) {
    return attrs["aria-label"];
  }
  return props.label || props.prefix || props.placeholder || undefined;
});

function focus(): void {
  inputEl.value?.focus();
}

defineExpose({ focus });
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <label v-if="label && !useShell" :for="inputId" class="text-label text-surface-sage">
      {{ label }}
    </label>

    <div v-if="useShell" :class="shellClass">
      <span
        v-if="prefix"
        class="relative z-10 shrink-0 pl-3 text-xs font-medium uppercase tracking-wide text-surface-mid"
      >
        {{ prefix }}
      </span>
      <input
        v-if="type === 'number'"
        :id="inputId"
        ref="inputEl"
        v-bind="inputAttrs"
        v-model.number="model"
        type="number"
        :aria-label="accessibleName"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="shellInputClass"
      />
      <input
        v-else
        :id="inputId"
        ref="inputEl"
        v-bind="inputAttrs"
        v-model="model"
        :type="type ?? 'text'"
        :aria-label="accessibleName"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="shellInputClass"
      />
      <span
        v-if="placeholder"
        :id="tipId"
        class="pointer-events-none absolute inset-y-0 right-3 z-0 flex items-center text-right text-xs text-surface-mid/40"
        aria-hidden="true"
      >
        {{ placeholder }}
      </span>
    </div>

    <template v-else>
      <input
        v-if="type === 'number'"
        :id="inputId"
        ref="inputEl"
        v-bind="inputAttrs"
        v-model.number="model"
        type="number"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="bareInputClass"
      />
      <input
        v-else
        :id="inputId"
        ref="inputEl"
        v-bind="inputAttrs"
        v-model="model"
        :type="type ?? 'text'"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="bareInputClass"
      />
    </template>

    <p v-if="error" :id="errorId" role="alert" class="text-xs text-status-error">
      {{ error }}
    </p>
    <p v-else-if="hint" :id="hintId" class="text-xs text-surface-mid">
      {{ hint }}
    </p>
  </div>
</template>
