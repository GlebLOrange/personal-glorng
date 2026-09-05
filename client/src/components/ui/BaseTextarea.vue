<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import {
  buildFieldAccessibleName,
  buildFieldDescribedBy,
  pickNativeAttrs,
} from "@/components/ui/fieldA11y";
import {
  FIELD_CLEAR_HIDDEN_CLASS,
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
    /** Optional left-side field name inside the control. */
    prefix?: string;
    label?: string;
    hint?: string;
    error?: string;
    rows?: number;
    compact?: boolean;
    /** Render the label inside the control instead of the outer border notch. */
    labelInside?: boolean;
  }>(),
  {
    labelInside: true,
  },
);

const attrs = useAttrs();
const fallbackId = useId();
const textareaId = computed(() => props.id ?? `base-textarea-${fallbackId}`);
const hintId = computed(() => `${textareaId.value}-hint`);
const errorId = computed(() => `${textareaId.value}-error`);
const tipId = computed(() => `${textareaId.value}-tip`);
const hasClearableValue = computed(() => Boolean(model.value?.length));
const useShell = computed(() =>
  Boolean(props.prefix || props.placeholder || props.labelInside || props.label),
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
  () => Boolean(props.placeholder) && !hasClearableValue.value && !showInsideLabel.value,
);
const tipInsetClass = computed(() => ["left-3", reserveClear.value ? "right-10" : "right-3"]);
const showLabelNotch = computed(() => Boolean(props.label) && !props.error && !props.labelInside);
const hasVisibleLabel = computed(
  () => showLabelNotch.value || Boolean(props.label && props.labelInside),
);
const showNotchRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
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
  props.error && "border-status-error",
]);
const shellClass = computed(() => [
  "relative flex w-full items-start rounded-lg border bg-surface-dark transition-colors",
  props.error
    ? "border-status-error"
    : "border-surface-border focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50",
]);
const shellTextareaClass = computed(() =>
  [
    "relative z-10 min-w-0 flex-1 resize-y border-0 bg-transparent px-3 text-left text-sm text-surface-light outline-none disabled:opacity-60",
    props.compact ? "min-h-9 py-1.5" : "min-h-10 py-2",
  ].join(" "),
);
const textareaAttrs = computed(() => pickNativeAttrs(attrs, ["aria-describedby"]));
const accessibleName = computed(() =>
  buildFieldAccessibleName({
    ariaLabel: attrs["aria-label"],
    hasVisibleLabel: hasVisibleLabel.value,
    label: props.label,
    prefix: props.prefix,
  }),
);
const notchBgClass = FIELD_NOTCH_BG_CLASS;
const notchClass = FIELD_NOTCH_CLASS;

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
      <label v-if="props.labelInside && props.label" :for="textareaId" class="sr-only">
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
        class="pointer-events-none absolute top-2.5 z-0 text-left text-xs font-medium text-surface-sage"
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
        {{ placeholder }}
      </span>
      <div
        v-if="reserveClear"
        class="absolute right-0 top-0 z-10 flex h-10 w-10 items-center justify-center"
        :class="showClear ? undefined : FIELD_CLEAR_HIDDEN_CLASS"
      >
        <IconCloseButton v-if="showClear" size="field" aria-label="clear" @click="clear" />
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
