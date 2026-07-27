<script setup lang="ts">
import { computed, useAttrs, useId } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import {
  buildFieldAccessibleName,
  buildFieldDescribedBy,
} from "@/components/ui/fieldA11y";
import {
  FIELD_NOTCH_BG_CLASS,
  FIELD_NOTCH_CLASS,
  FIELD_NOTCH_ROW_CLASS,
  FIELD_WRAPPER_CLASS,
  SELECT_CLASS,
  SELECT_CLASS_COMPACT,
} from "@/constants/formClasses";

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
const showLabelNotch = computed(() => Boolean(props.label) && !props.error);
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
const selectClass = computed(() => (props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS));
const ariaLabel = computed(() =>
  buildFieldAccessibleName({
    ariaLabel: attrs["aria-label"],
    hasVisibleLabel: showLabelNotch.value,
    label: props.label,
  }),
);
const notchBgClass = FIELD_NOTCH_BG_CLASS;
const notchClass = FIELD_NOTCH_CLASS;
</script>

<template>
  <div
    :class="[FIELD_WRAPPER_CLASS, hasBorderNotch ? 'pt-2.5' : undefined, attrs.class]"
  >
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
    <div
      v-if="showNotchRow"
      :class="[FIELD_NOTCH_ROW_CLASS, notchBgClass]"
    >
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="selectId"
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
