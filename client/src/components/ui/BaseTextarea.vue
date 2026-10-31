<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import {
  buildFieldAccessibleName,
  buildFieldDescribedBy,
  pickNativeAttrs,
  resolveFieldCopy,
} from "@/components/ui/fieldA11y";
import {
  FIELD_CLEAR_HIDDEN_CLASS,
  FIELD_LABEL_TEXT_CLASS,
  FIELD_NOTCH_BG_CLASS,
  FIELD_NOTCH_CLASS,
  FIELD_NOTCH_ROW_CLASS,
  FIELD_WRAPPER_CLASS,
  TEXTAREA_CLASS,
  TEXTAREA_CLASS_COMPACT,
} from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string>();

const props = withDefaults(
  defineProps<{
    id?: string;
    /** Faint tip drawn behind the value (full-width textarea). */
    placeholder?: string;
    /** Explicit overlay tip; preferred over `placeholder` when both are set. */
    tip?: string;
    /** Optional left-side field name inside the control. */
    prefix?: string;
    label?: string;
    hint?: string;
    error?: string;
    rows?: number;
    compact?: boolean;
    /** Render the label inside the control instead of the trailing / notch title. */
    labelInside?: boolean;
    /**
     * When not labelInside: `end` = no visible name (sr-only / aria; default);
     * `start` = border notch (opt-in).
     */
    labelAlign?: "start" | "end";
    /** Shrink shell/textarea to content (tool action panels) instead of w-full. */
    autoWidth?: boolean;
  }>(),
  {
    labelInside: false,
    labelAlign: "end",
    autoWidth: false,
  },
);

const attrs = useAttrs();
const fallbackId = useId();
const textareaId = computed(() => props.id ?? `base-textarea-${fallbackId}`);
const hintId = computed(() => `${textareaId.value}-hint`);
const errorId = computed(() => `${textareaId.value}-error`);
const tipId = computed(() => `${textareaId.value}-tip`);
const fieldCopy = computed(() => resolveFieldCopy(props.label, props.placeholder, props.tip));
const hasClearableValue = computed(() => Boolean(model.value?.length));
const isInlineEnd = computed(() => props.labelAlign === "end" && !props.labelInside);
const useShell = computed(() =>
  Boolean(
    props.prefix ||
    fieldCopy.value.tip ||
    props.placeholder ||
    props.labelInside ||
    props.label ||
    isInlineEnd.value,
  ),
);
/** Reserve clear width whenever shell is active so tip never jumps vs BaseInput. */
const reserveClear = computed(() => useShell.value);
const showClear = computed(() => reserveClear.value && hasClearableValue.value);
/** Inside-label overlay mirrors tip: visible only while empty. */
const showInsideLabel = computed(
  () => Boolean(props.labelInside && props.label) && !hasClearableValue.value,
);
/** Tip only when empty and no inside label is showing. */
const showTip = computed(
  () => Boolean(fieldCopy.value.tip) && !hasClearableValue.value && !showInsideLabel.value,
);
const tipInsetClass = computed(() => [
  "left-3",
  reserveClear.value || isInlineEnd.value ? "right-10" : "right-3",
]);
const showLabelNotch = computed(() => Boolean(props.label) && !props.error && !props.labelInside);
/** Border-notch / labelInside / end-mode sr-only — all count as a named control. */
const hasVisibleLabel = computed(
  () =>
    showLabelNotch.value ||
    Boolean(props.label && props.labelInside) ||
    (isInlineEnd.value && Boolean(props.label) && !props.error),
);
const showLabelRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
/** End alignment: only reserve trailing chrome for FieldHelp (no visible field name). */
const showInlineEndLabel = computed(() => isInlineEnd.value && Boolean(props.hint && !props.error));
const showNotchRow = computed(() => !isInlineEnd.value && showLabelRow.value);
const showSrOnlyLabel = computed(
  () => Boolean(props.label) && (props.labelInside || (isInlineEnd.value && !props.error)),
);
const hasBorderNotch = computed(() => showNotchRow.value || Boolean(props.error));
const describedBy = computed(() =>
  buildFieldDescribedBy({
    ariaDescribedBy: attrs["aria-describedby"],
    hint: props.hint,
    hintId: hintId.value,
    error: props.error,
    errorId: errorId.value,
  }),
);
const bareClass = computed(() => [
  props.compact ? TEXTAREA_CLASS_COMPACT : TEXTAREA_CLASS,
  props.autoWidth && "!w-auto max-w-full",
  props.error && "border-status-error",
]);
const shellClass = computed(() => [
  // Inset ring (not border) — matches BaseInput field chrome.
  "relative flex items-start rounded-lg bg-surface-dark transition-colors",
  props.autoWidth ? "w-auto max-w-full" : "w-full",
  showInlineEndLabel.value && props.hint ? "overflow-visible" : "overflow-hidden",
  props.error
    ? "ring-1 ring-inset ring-status-error focus-within:ring-status-error"
    : "ring-1 ring-inset ring-surface-border focus-within:ring-2 focus-within:ring-accent-coral/50",
]);
const shellTextareaClass = computed(() =>
  [
    "relative z-10 min-w-0 flex-1 resize-y border-0 bg-transparent px-3 text-left text-sm text-surface-light outline-none disabled:opacity-60",
    props.compact ? "min-h-9 py-1.5" : "min-h-11 py-2",
  ].join(" "),
);
const textareaAttrs = computed(() => {
  const native = pickNativeAttrs(attrs, ["aria-describedby"]);
  const callerTitle = typeof native.title === "string" ? native.title : undefined;
  return {
    ...native,
    title: callerTitle ?? fieldCopy.value.name,
  };
});
const accessibleName = computed(() =>
  buildFieldAccessibleName({
    ariaLabel: attrs["aria-label"],
    hasVisibleLabel: hasVisibleLabel.value,
    label: props.label,
    prefix: props.prefix,
    placeholder: props.placeholder,
  }),
);
const notchBgClass = FIELD_NOTCH_BG_CLASS;
const notchClass = FIELD_NOTCH_CLASS;
const helpAlign = computed(() => (isInlineEnd.value ? "end" : "start"));
const helpPlacement = computed<"bottom" | "top">(() => (isInlineEnd.value ? "top" : "bottom"));

function clear(): void {
  model.value = "";
}
</script>

<template>
  <div
    :class="[FIELD_WRAPPER_CLASS, hasBorderNotch ? 'pt-2.5' : undefined, $attrs.class]"
    :style="$attrs.style"
  >
    <div v-if="useShell" :class="shellClass">
      <span
        v-if="prefix"
        class="relative z-10 shrink-0 pl-3 pt-2.5 text-xs font-medium text-surface-mid"
      >
        {{ prefix }}
      </span>
      <label v-if="showSrOnlyLabel" :for="textareaId" class="sr-only">
        {{ props.label }}
      </label>
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
        v-if="showInsideLabel"
        aria-hidden="true"
        class="pointer-events-none absolute top-2.5 z-0 text-left text-xs font-medium text-surface-muted"
        :class="tipInsetClass"
      >
        {{ label }}
      </span>
      <span
        v-if="showTip"
        :id="tipId"
        class="pointer-events-none absolute top-2.5 z-0 text-left text-xs text-surface-mid/65"
        :class="tipInsetClass"
        aria-hidden="true"
      >
        {{ fieldCopy.tip }}
      </span>
      <div
        v-if="reserveClear || showInlineEndLabel"
        class="absolute right-0 top-0 z-10 flex h-11 items-center gap-0.5 pr-2"
      >
        <div v-if="showInlineEndLabel" class="flex max-w-[11rem] items-center gap-1 bg-transparent">
          <FieldHelp
            size="sm"
            :align="helpAlign"
            :placement="helpPlacement"
            :text="hint ?? ''"
            :content-id="hintId"
          />
        </div>
        <div
          v-if="reserveClear"
          class="flex h-11 w-11 items-center justify-center"
          :class="showClear ? undefined : FIELD_CLEAR_HIDDEN_CLASS"
        >
          <IconCloseButton v-if="showClear" size="field" aria-label="clear" @click="clear" />
        </div>
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

    <div v-if="showNotchRow" :class="[FIELD_NOTCH_ROW_CLASS, notchBgClass]">
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="textareaId"
        :class="['pointer-events-auto truncate', FIELD_LABEL_TEXT_CLASS]"
      >
        {{ label }}
      </label>
      <span class="pointer-events-auto">
        <FieldHelp v-if="hint" size="sm" :align="helpAlign" :text="hint" :content-id="hintId" />
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
