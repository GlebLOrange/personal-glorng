<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import { TEXTAREA_CLASS, TEXTAREA_CLASS_COMPACT } from "@/constants/formClasses";

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
  reserveClear.value ? "right-11" : "right-3",
]);
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
      props.compact ? "min-h-9 py-1.5" : "min-h-11 py-2",
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
  // Visible <label for> names the control when label is set.
  if (props.label) return undefined;
  // Tip/placeholder is visual help only (aria-hidden) — never the accessible name.
  return props.prefix || undefined;
});

function clear(): void {
  model.value = "";
}
</script>

<template>
  <div class="relative flex min-w-0 flex-col gap-1" :class="$attrs.class" :style="$attrs.style">
    <div v-if="label || hint" class="flex items-center gap-1.5">
      <!-- associated via :for / :id (computed ids); FieldHelp sits beside the label -->
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label v-if="label" :for="textareaId" class="text-label text-surface-sage">
        {{ label }}
      </label>
      <FieldHelp v-if="hint" :text="hint" :content-id="hintId" />
    </div>

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
        class="absolute right-0 top-0 z-10 flex w-11 items-center justify-center"
        :class="showClear ? undefined : 'invisible pointer-events-none'"
      >
        <IconCloseButton aria-label="Clear" @click="clear" />
      </div>
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

    <!-- ponytail: absolute above control so validation never shifts following fields -->
    <p
      v-if="error"
      :id="errorId"
      role="alert"
      class="pointer-events-none absolute bottom-full left-0 right-0 z-10 mb-1 text-center text-xs leading-4 text-status-error"
    >
      {{ error }}
    </p>
  </div>
</template>
