<script setup lang="ts">
import { computed, nextTick, ref, useAttrs, useId } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import SearchIcon from "@/components/icons/SearchIcon.vue";
import { pickNativeAttrs } from "@/components/ui/fieldA11y";
import {
  CONTROL_SIZE,
  FIELD_CLEAR_HIDDEN_CLASS,
  FIELD_CLEAR_SLOT,
  FIELD_WRAPPER_CLASS,
} from "@/constants/formClasses";
import { SEARCH_MIN_QUERY_LENGTH } from "@/constants/search";

defineOptions({ inheritAttrs: false });

const model = defineModel<string>({ default: "" });

const props = withDefaults(
  defineProps<{
    id?: string;
    /** In-bar overlay label (decorative); not the accessible name. */
    placeholder?: string;
    /** Accessible name when placeholder is decorative. */
    ariaLabel?: string;
    /** HTML minlength hint; search APIs gate at SEARCH_MIN_QUERY_LENGTH. */
    minLength?: number;
    /** Shrink control to content (tool action panels) instead of w-full. */
    autoWidth?: boolean;
    /** Collapse to a left-aligned search-icon button; click expands to full width. */
    collapsible?: boolean;
  }>(),
  {
    collapsible: false,
    minLength: SEARCH_MIN_QUERY_LENGTH,
    autoWidth: false,
  },
);

const attrs = useAttrs();
const fallbackId = useId();
const inputId = computed(() => props.id ?? `search-input-${fallbackId}`);
const overlayId = computed(() => `${inputId.value}-overlay`);
/** Raw length — a space counts as typed so the overlay hides. */
const hasValue = computed(() => model.value.length > 0);
const showOverlay = computed(() => Boolean(props.placeholder) && !hasValue.value);
/** Decorative placeholder is not the accessible name. */
const accessibleName = computed(() => props.ariaLabel || "search");
const inputAttrs = computed(() => pickNativeAttrs(attrs));

const inputEl = ref<HTMLInputElement | null>(null);
const expandedState = ref(false);
const collapsed = computed(() => props.collapsible && !expandedState.value && !hasValue.value);

async function expand(): Promise<void> {
  expandedState.value = true;
  await nextTick();
  inputEl.value?.focus();
}

function onFocusOut(event: FocusEvent): void {
  if (!props.collapsible || hasValue.value) return;
  const root = event.currentTarget as HTMLElement | null;
  if (root && event.relatedTarget instanceof Node && root.contains(event.relatedTarget)) return;
  expandedState.value = false;
}

function clear(): void {
  model.value = "";
  if (props.collapsible) void nextTick(() => inputEl.value?.focus());
}
</script>

<template>
  <button
    v-if="collapsed"
    type="button"
    :aria-label="accessibleName"
    :aria-controls="inputId"
    aria-expanded="false"
    :class="[
      $attrs.class,
      CONTROL_SIZE,
      '!w-11 !flex-none shrink-0 self-start inline-flex items-center justify-center rounded-lg bg-surface-dark text-surface-mid ring-1 ring-inset ring-surface-border transition-colors hover:text-surface-light focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-coral/50',
    ]"
    @click="expand"
  >
    <SearchIcon class-name="size-4" />
  </button>
  <div
    v-else
    :class="[
      FIELD_WRAPPER_CLASS,
      CONTROL_SIZE,
      'flex items-center overflow-hidden rounded-lg bg-surface-dark transition-colors ring-1 ring-inset ring-surface-border focus-within:ring-2 focus-within:ring-accent-coral/50',
      props.collapsible
        ? 'w-full min-w-0 flex-1'
        : props.autoWidth
          ? 'w-auto max-w-full'
          : 'w-full',
      $attrs.class,
    ]"
    @focusout="onFocusOut"
  >
    <span class="relative z-10 flex shrink-0 items-center pl-3 text-surface-mid" aria-hidden="true">
      <SearchIcon class-name="size-4" />
    </span>
    <div class="relative z-10 flex h-full min-w-0 flex-1 items-center">
      <input
        :id="inputId"
        ref="inputEl"
        v-model="model"
        type="search"
        :minlength="minLength"
        :aria-label="accessibleName"
        class="search-input-field relative z-10 h-full min-w-0 w-full border-0 bg-transparent py-0 pl-2.5 pr-1 text-left text-sm text-surface-light outline-none"
        v-bind="inputAttrs"
        @keydown.esc="collapsible && !hasValue ? (expandedState = false) : undefined"
      />
      <span
        v-if="showOverlay"
        :id="overlayId"
        class="pointer-events-none absolute inset-y-0 left-2.5 right-1 z-0 flex items-center"
        aria-hidden="true"
      >
        <span class="min-w-0 truncate text-sm text-surface-mid/50">
          {{ placeholder }}
        </span>
      </span>
    </div>
    <!-- Reserved clear slot — always present so overlay/value never shift. -->
    <div :class="[FIELD_CLEAR_SLOT, hasValue ? undefined : FIELD_CLEAR_HIDDEN_CLASS]">
      <IconCloseButton v-if="hasValue" size="field" aria-label="clear search" @click="clear" />
    </div>
  </div>
</template>

<style scoped>
.search-input-field::-webkit-search-cancel-button,
.search-input-field::-webkit-search-decoration {
  -webkit-appearance: none;
  appearance: none;
}
</style>
