<script setup lang="ts">
import { computed, useId } from "vue";

import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import SearchIcon from "@/components/icons/SearchIcon.vue";

defineOptions({ inheritAttrs: false });

const model = defineModel<string>({ default: "" });

const props = defineProps<{
  id?: string;
  placeholder?: string;
  /** Accessible name when placeholder is decorative. */
  ariaLabel?: string;
}>();

const fallbackId = useId();
const inputId = computed(() => props.id ?? `search-input-${fallbackId}`);
const hasValue = computed(() => Boolean(model.value.trim()));
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
    <input
      :id="inputId"
      v-model="model"
      type="search"
      :placeholder="placeholder"
      :aria-label="accessibleName"
      class="search-input-field relative z-10 h-full min-w-0 flex-1 border-0 bg-transparent py-0 pl-2.5 text-left text-sm text-surface-light outline-none placeholder:text-surface-mid/50"
      :class="hasValue ? 'pr-1' : 'pr-3'"
      v-bind="{
        ...Object.fromEntries(
          Object.entries($attrs).filter(([key]) => key !== 'class' && key !== 'style'),
        ),
      }"
    />
    <div v-if="hasValue" class="relative z-10 flex shrink-0 items-center pr-0.5">
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
