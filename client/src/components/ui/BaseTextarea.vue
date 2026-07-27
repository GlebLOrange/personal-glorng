<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import {
  TEXTAREA_CLASS,
  TEXTAREA_CLASS_COMPACT,
} from "@/constants/formClasses";

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
  compact?: boolean;
}>();

const attrs = useAttrs();
const fallbackId = useId();
const textareaId = computed(() => props.id ?? `base-textarea-${fallbackId}`);
const hintId = computed(() => `${textareaId.value}-hint`);
const errorId = computed(() => `${textareaId.value}-error`);
const tipId = computed(() => `${textareaId.value}-tip`);
const hasClearableValue = computed(() => Boolean(model.value?.length));
const useShell = computed(() => Boolean(props.prefix || props.placeholder));
/** Reserve clear width whenever shell is active so tip never jumps vs BaseInput. */
const reserveClear = computed(() => useShell.value);
const showClear = computed(() => reserveClear.value && hasClearableValue.value);
/** Tip only when empty; hide while typing (Clear X takes the right side). */
const showTip = computed(() => Boolean(props.placeholder) && !hasClearableValue.value);
const tipInsetClass = computed(() => [
  "left-3",
  reserveClear.value ? "right-10" : "right-3",
]);
const showLabelNotch = computed(() => Boolean(props.label) && !props.error);
const showNotchRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
const hasBorderNotch = computed(() => showNotchRow.value || Boolean(props.error));
const describedBy = computed(() => {
  const ids: string[] = [];
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  // Visual tip stays aria-hidden; do not wire into describedby.
  return ids.length ? ids.join(" ") : undefined;
});
const bareClass = computed(() => [
  props.compact ? TEXTAREA_CLASS_COMPACT : TEXTAREA_CLASS,
  props.error && "border-status-error",
]);
const shellClass = computed(() => [
  "relative flex w-full items-start rounded-lg border bg-surface-dark transition-colors",
  props.error
    ? "border-status-error"
    : "border-surface-border focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50",
]);
const shellTextareaClass = computed(
  () =>
    [
      "relative z-10 min-w-0 flex-1 resize-y border-0 bg-transparent px-3 text-left text-sm text-surface-light outline-none disabled:opacity-60",
      props.compact ? "min-h-9 py-1.5" : "min-h-10 py-2",
    ].join(" "),
);
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
  if (showLabelNotch.value) return undefined;
  if (props.label) return props.label;
  // Tip/placeholder is visual help only (aria-hidden) — never the accessible name.
  return props.prefix || undefined;
});
const notchBgClass = "bg-surface-card";
const notchClass =
  "pointer-events-none absolute left-3 top-2.5 z-20 max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] truncate px-1.5 text-xs leading-4";

function clear(): void {
  model.value = "";
}
</script>

<template>
  <div
    class="relative min-w-0"
    :class="[hasBorderNotch ? 'pt-2.5' : undefined, $attrs.class]"
    :style="$attrs.style"
  >
    <div v-if="useShell" :class="shellClass">
      <span
        v-if="prefix"
        class="relative z-10 shrink-0 pl-3 pt-2.5 text-xs font-medium text-surface-mid"
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
        v-if="showTip"
        :id="tipId"
        class="pointer-events-none absolute top-2.5 z-0 text-left text-xs text-surface-mid/65"
        :class="tipInsetClass"
        aria-hidden="true"
      >
        {{ placeholder }}
      </span>
      <div
        v-if="reserveClear"
        class="absolute right-0 top-0 z-10 flex h-10 w-10 items-center justify-center"
        :class="showClear ? undefined : 'invisible pointer-events-none'"
      >
        <IconCloseButton size="field" aria-label="Clear" @click="clear" />
      </div>
    </div>

    <div v-else class="relative">
      <textarea
        :id="textareaId"
        v-bind="textareaAttrs"
        v-model="model"
        :rows="rows ?? 5"
        :aria-label="accessibleName"
        :aria-invalid="error ? true : undefined"
        :aria-describedby="describedBy"
        :class="bareClass"
      />
    </div>

    <div
      v-if="showNotchRow"
      class="absolute left-3 top-2.5 z-20 flex max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] items-center gap-1 px-1.5"
      :class="notchBgClass"
    >
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="textareaId"
        class="pointer-events-auto truncate text-label leading-4 text-surface-sage"
      >
        {{ label }}
      </label>
      <span class="pointer-events-auto">
        <FieldHelp v-if="hint" :text="hint" :content-id="hintId" />
      </span>
    </div>
    <p
      v-if="error"
      :id="errorId"
      role="alert"
      :class="[notchClass, notchBgClass, 'text-status-error']"
    >
      {{ error }}
    </p>
  </div>
</template>
