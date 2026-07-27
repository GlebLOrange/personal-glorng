<script setup lang="ts">
import { computed, useId } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import SearchIcon from "@/components/icons/SearchIcon.vue";
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
  }>(),
  {
    minLength: SEARCH_MIN_QUERY_LENGTH,
  },
);

const fallbackId = useId();
const inputId = computed(() => props.id ?? `search-input-${fallbackId}`);
const overlayId = computed(() => `${inputId.value}-overlay`);
/** Raw length — a space counts as typed so the overlay hides. */
const hasValue = computed(() => model.value.length > 0);
const showOverlay = computed(() => Boolean(props.placeholder) && !hasValue.value);
/** Decorative placeholder is not the accessible name. */
const accessibleName = computed(() => props.ariaLabel || "Search");

function clear(): void {
  model.value = "";
}
</script>

<template>
  <div
    class="relative flex h-11 w-full min-w-0 items-center rounded-lg border border-surface-border bg-surface-dark transition-colors focus-within:border-accent-blue focus-within:ring-2 focus-within:ring-accent-blue/50"
    :class="$attrs.class"
  >
    <span class="relative z-10 flex shrink-0 items-center pl-3 text-surface-mid" aria-hidden="true">
      <SearchIcon class-name="size-4" />
    </span>
    <div class="relative z-10 flex h-full min-w-0 flex-1 items-center">
      <input
        :id="inputId"
        v-model="model"
        type="search"
        :minlength="minLength"
        :aria-label="accessibleName"
        class="search-input-field relative z-10 h-full min-w-0 w-full border-0 bg-transparent py-0 pl-2.5 pr-1 text-left text-sm text-surface-light outline-none"
        v-bind="{
          ...Object.fromEntries(
            Object.entries($attrs).filter(([key]) => key !== 'class' && key !== 'style'),
          ),
        }"
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
    <div
      class="relative z-10 flex w-11 shrink-0 items-center justify-center"
      :class="hasValue ? undefined : 'invisible pointer-events-none'"
    >
      <IconCloseButton aria-label="Clear search" @click="clear" />
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
