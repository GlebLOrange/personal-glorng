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
const showLabelNotch = computed(() => Boolean(props.label) && !props.error);
const showNotchRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
const hasBorderNotch = computed(() => showNotchRow.value || Boolean(props.error));
const describedBy = computed(() => {
  const ids: string[] = [];
  if (props.error) ids.push(errorId.value);
  else if (props.hint) ids.push(hintId.value);
  return ids.length ? ids.join(" ") : undefined;
});
const selectClass = computed(() => (props.compact ? SELECT_CLASS_COMPACT : SELECT_CLASS));
const ariaLabel = computed(() => {
  if (typeof attrs["aria-label"] === "string" && attrs["aria-label"].trim()) {
    return attrs["aria-label"];
  }
  if (showLabelNotch.value) return undefined;
  if (props.label) return props.label;
  return undefined;
});
const notchBgClass = "bg-surface-card";
const notchClass =
  "pointer-events-none absolute left-3 top-2.5 z-20 max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] truncate px-1.5 text-xs leading-4";
</script>

<template>
  <div
    class="relative min-w-0"
    :class="[hasBorderNotch ? 'pt-2.5' : undefined, attrs.class]"
  >
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
    <div
      v-if="showNotchRow"
      class="absolute left-3 top-2.5 z-20 flex max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] items-center gap-1 px-1.5"
      :class="notchBgClass"
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
