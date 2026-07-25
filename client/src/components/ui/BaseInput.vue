<script setup lang="ts">
import { computed, ref, useAttrs, useId, useSlots } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
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
  /** Border tone when there is no error message (validation UI). */
  tone?: "error" | "success";
  compact?: boolean;
}>();

const attrs = useAttrs();
const slots = useSlots();
const inputEl = ref<HTMLInputElement | null>(null);
const fallbackId = useId();
const inputId = computed(() => props.id ?? `base-input-${fallbackId}`);
const hintId = computed(() => `${inputId.value}-hint`);
const errorId = computed(() => `${inputId.value}-error`);
const tipId = computed(() => `${inputId.value}-tip`);
const hasSuffix = computed(() => Boolean(slots.suffix));
const isClearableType = computed(() => props.type !== "number");
const hasClearableValue = computed(() => {
  if (!isClearableType.value) return false;
  const value = model.value;
  return typeof value === "string" && value.length > 0;
});
const useShell = computed(() => Boolean(props.prefix || props.placeholder || hasSuffix.value));
const showClear = computed(() => useShell.value && hasClearableValue.value);
const showTip = computed(() => Boolean(props.placeholder));
const tipInsetClass = computed(() =>
  showClear.value || hasSuffix.value ? "right-11" : "right-3",
);
const describedBy = computed(() => {
  const ids: string[] = [];
  const fromAttrs = attrs["aria-describedby"];
  if (typeof fromAttrs === "string" && fromAttrs.trim()) {
    ids.push(...fromAttrs.trim().split(/\s+/));
  }
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  // Visual tip stays aria-hidden; do not wire into describedby.
  return ids.length ? [...new Set(ids)].join(" ") : undefined;
});
const borderTone = computed<"error" | "success" | "idle">(() => {
  if (props.error || props.tone === "error") return "error";
  if (props.tone === "success") return "success";
  return "idle";
});
const toneBorderClass = computed(() => {
  if (borderTone.value === "error") return "border-status-error";
  if (borderTone.value === "success") return "border-status-success";
  return undefined;
});
const bareInputClass = computed(() => [
  props.compact ? FIELD_INPUT_CLASS_COMPACT : FIELD_INPUT_CLASS,
  props.type === "number" && "font-data",
  toneBorderClass.value,
]);
const shellClass = computed(() => [
  "relative flex w-full items-center rounded-lg border bg-surface-dark transition-colors",
  props.compact ? "h-9" : "h-11",
  toneBorderClass.value ??
    "border-surface-border focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50",
]);
const shellInputClass = computed(() => [
  "relative z-10 h-full min-w-0 flex-1 border-0 bg-transparent px-3 text-left text-sm text-surface-light outline-none",
  props.type === "number" && "font-data",
  props.type === "search" && "base-input-search",
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
  // Visible <label for> names the control when label is set.
  if (props.label) return undefined;
  return props.prefix || props.placeholder || undefined;
});

function clear(): void {
  model.value = "";
}

function focus(): void {
  inputEl.value?.focus();
}

defineExpose({ focus });
</script>

<template>
  <div class="flex flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <label v-if="label" :for="inputId" class="text-label text-surface-sage">
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
        :aria-invalid="borderTone === 'error' ? true : undefined"
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
        :aria-invalid="borderTone === 'error' ? true : undefined"
        :aria-describedby="describedBy"
        :class="shellInputClass"
      />
      <span
        v-if="showTip"
        :id="tipId"
        class="pointer-events-none absolute inset-y-0 z-0 flex items-center text-right text-xs text-surface-mid/65"
        :class="tipInsetClass"
        aria-hidden="true"
      >
        {{ placeholder }}
      </span>
      <div
        v-if="showClear || hasSuffix"
        class="relative z-10 flex shrink-0 items-center gap-0.5 pr-1"
      >
        <slot name="suffix" />
        <IconCloseButton v-if="showClear" aria-label="Clear" @click="clear" />
      </div>
    </div>

    <template v-else>
      <input
        v-if="type === 'number'"
        :id="inputId"
        ref="inputEl"
        v-bind="inputAttrs"
        v-model.number="model"
        type="number"
        :aria-invalid="borderTone === 'error' ? true : undefined"
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
        :aria-invalid="borderTone === 'error' ? true : undefined"
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

<style scoped>
.base-input-search::-webkit-search-cancel-button,
.base-input-search::-webkit-search-decoration {
  -webkit-appearance: none;
  appearance: none;
}
</style>
