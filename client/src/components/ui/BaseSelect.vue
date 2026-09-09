<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import { buildFieldAccessibleName, buildFieldDescribedBy } from "@/components/ui/fieldA11y";
import {
  FIELD_INLINE_END_LABEL_CLASS,
  FIELD_LABEL_TEXT_CLASS,
  FIELD_NOTCH_BG_CLASS,
  FIELD_NOTCH_CLASS,
  FIELD_NOTCH_ROW_CLASS,
  FIELD_WRAPPER_CLASS,
  SELECT_CLASS,
  SELECT_CLASS_COMPACT,
  SELECT_INLINE_END_PAD_CLASS,
  SELECT_INLINE_END_PAD_COMPACT_CLASS,
} from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string | number | null>();

const props = withDefaults(
  defineProps<{
    id?: string;
    label?: string;
    hint?: string;
    error?: string;
    compact?: boolean;
    /**
     * `start` — border-notch label (default).
     * `end` — label + help inside the control, left of the chevron.
     */
    labelAlign?: "start" | "end";
  }>(),
  { labelAlign: "start" },
);

const attrs = useAttrs();
const fallbackId = useId();
const selectId = computed(() => props.id ?? `base-select-${fallbackId}`);
const hintId = computed(() => `${selectId.value}-hint`);
const errorId = computed(() => `${selectId.value}-error`);
const isInlineEnd = computed(() => props.labelAlign === "end");
const showLabelNotch = computed(() => Boolean(props.label) && !props.error);
const showLabelRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
const showInlineEndLabel = computed(() => isInlineEnd.value && showLabelRow.value);
const showBorderNotchRow = computed(() => !isInlineEnd.value && showLabelRow.value);
const hasBorderNotch = computed(() => showBorderNotchRow.value || Boolean(props.error));
const describedBy = computed(() =>
  buildFieldDescribedBy({
    ariaDescribedBy: attrs["aria-describedby"],
    hint: props.hint,
    hintId: hintId.value,
    error: props.error,
    errorId: errorId.value,
  }),
);
const selectClass = computed(() => {
  const base = props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS;
  if (!showInlineEndLabel.value) return base;
  const pad = props.compact ? SELECT_INLINE_END_PAD_COMPACT_CLASS : SELECT_INLINE_END_PAD_CLASS;
  return `${base} ${pad}`;
});
const ariaLabel = computed(() =>
  buildFieldAccessibleName({
    ariaLabel: attrs["aria-label"],
    hasVisibleLabel: showLabelNotch.value,
    label: props.label,
  }),
);
const notchBgClass = FIELD_NOTCH_BG_CLASS;
const helpAlign = computed(() => (isInlineEnd.value ? "end" : "start"));
</script>

<template>
  <div :class="[FIELD_WRAPPER_CLASS, hasBorderNotch ? 'pt-2.5' : undefined, attrs.class]">
    <select
      :id="selectId"
      v-model="model"
      :aria-label="ariaLabel"
      :aria-invalid="error ? true : undefined"
      :aria-describedby="describedBy"
      :class="[
        selectClass,
        'w-full',
        error ? 'ring-status-error focus-visible:ring-status-error' : undefined,
      ]"
    >
      <slot />
    </select>
    <div v-if="showInlineEndLabel" :class="FIELD_INLINE_END_LABEL_CLASS">
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="selectId"
        :class="['pointer-events-auto truncate', FIELD_LABEL_TEXT_CLASS]"
      >
        {{ label }}
      </label>
      <span class="pointer-events-auto">
        <FieldHelp
          v-if="hint"
          size="sm"
          :align="helpAlign"
          :text="hint"
          :content-id="hintId"
        />
      </span>
    </div>
    <div v-else-if="showBorderNotchRow" :class="[FIELD_NOTCH_ROW_CLASS, notchBgClass]">
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="selectId"
        :class="['pointer-events-auto truncate', FIELD_LABEL_TEXT_CLASS]"
      >
        {{ label }}
      </label>
      <span class="pointer-events-auto">
        <FieldHelp
          v-if="hint"
          size="sm"
          :align="helpAlign"
          :text="hint"
          :content-id="hintId"
        />
      </span>
    </div>
    <p
      v-if="error"
      :id="errorId"
      role="alert"
      :class="[FIELD_NOTCH_CLASS, notchBgClass, 'text-status-error']"
    >
      {{ error }}
    </p>
  </div>
</template>
