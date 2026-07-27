<script setup lang="ts">
import { computed, ref, useAttrs, useId, useSlots } from "vue";

import FieldHelp from "@/components/ui/FieldHelp.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import {
  FIELD_CLEAR_SLOT,
  FIELD_INPUT_CLASS,
  FIELD_INPUT_CLASS_COMPACT,
} from "@/constants/formClasses";

defineOptions({ inheritAttrs: false });

const model = defineModel<string | number | null>();

const props = defineProps<{
  id?: string;
  type?: string;
  /** In-bar overlay tip (decorative); shown only when empty. Not the accessible name. */
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
const hasTypedValue = computed(() => {
  if (typeof model.value === "string") return model.value.length > 0;
  if (typeof model.value === "number") return true;
  return false;
});
const hasClearableValue = computed(() => isClearableType.value && hasTypedValue.value);
const useShell = computed(() => Boolean(props.prefix || props.placeholder || hasSuffix.value));
const showClear = computed(() => useShell.value && hasClearableValue.value);
/** Reserve clear width whenever shell is clearable so tip/value never jump. */
const reserveClear = computed(() => useShell.value && isClearableType.value);
/** Overlay tip only when empty (even if focused). */
const showTip = computed(() => Boolean(props.placeholder) && !hasTypedValue.value);
const tipInsetClass = computed(() => [
  "left-3",
  reserveClear.value || hasSuffix.value ? "right-10" : "right-3",
]);
/** Error replaces label on the border notch; hint rides beside the label when present. */
const showLabelNotch = computed(() => Boolean(props.label) && !props.error);
const showNotchRow = computed(() => showLabelNotch.value || Boolean(props.hint && !props.error));
const hasBorderNotch = computed(() => showNotchRow.value || Boolean(props.error));
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
  // No overflow clip — clear may sit flush; notches live on the outer wrapper.
  "relative flex w-full items-center rounded-lg border bg-surface-dark transition-colors",
  props.compact ? "h-9" : "h-10",
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
  // Visible <label for> names the control when label notch is shown.
  if (showLabelNotch.value) return undefined;
  // Error hides the notch label — keep the name via aria-label.
  if (props.label) return props.label;
  // Tip/placeholder is visual help only (aria-hidden) — never the accessible name.
  return props.prefix || undefined;
});
/**
 * Notch sits on the field’s top border against the parent surface (usually card).
 * Shell fill is surface-dark — do not use that here or the chip looks wrong on cards/modals.
 */
const notchBgClass = "bg-surface-card";
/** Shared notch chrome — mostly above the border so value text is never covered. */
const notchClass =
  "pointer-events-none absolute left-3 top-2.5 z-20 max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] truncate px-1.5 text-xs leading-4";

function clear(): void {
  model.value = "";
}

function focus(): void {
  inputEl.value?.focus();
}

defineExpose({ focus });
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
        class="relative z-10 shrink-0 pl-3 text-xs font-medium text-surface-mid"
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
        class="pointer-events-none absolute inset-y-0 z-0 flex items-center"
        :class="tipInsetClass"
        aria-hidden="true"
      >
        <span class="min-w-0 flex-1 truncate text-left text-xs text-surface-mid/65">
          {{ placeholder }}
        </span>
      </span>
      <div
        v-if="reserveClear || hasSuffix"
        class="relative z-10 flex shrink-0 items-center gap-0.5 self-stretch"
      >
        <slot name="suffix" />
        <div
          v-if="reserveClear"
          :class="[FIELD_CLEAR_SLOT, showClear ? undefined : 'invisible pointer-events-none']"
        >
          <IconCloseButton size="field" aria-label="Clear" @click="clear" />
        </div>
      </div>
    </div>

    <div v-else class="relative">
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
        :class="bareInputClass"
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
        :class="bareInputClass"
      />
    </div>

    <!-- Outside the control box so scroll/overflow parents cannot clip the notch into the value. -->
    <div
      v-if="showNotchRow"
      class="absolute left-3 top-2.5 z-20 flex max-w-[calc(100%-1.5rem)] -translate-y-[calc(100%-3px)] items-center gap-1 px-1.5"
      :class="notchBgClass"
    >
      <!-- associated via :for / :id; FieldHelp sits beside the label -->
      <!-- eslint-disable-next-line vuejs-accessibility/label-has-for -->
      <label
        v-if="showLabelNotch"
        :for="inputId"
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

<style scoped>
.base-input-search::-webkit-search-cancel-button,
.base-input-search::-webkit-search-decoration {
  -webkit-appearance: none;
  appearance: none;
}
</style>
