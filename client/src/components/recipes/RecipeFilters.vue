<script setup lang="ts">
import { computed } from "vue";

import AdminFilterDropdown from "@/components/admin/AdminFilterDropdown.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";

const props = defineProps<{
  search: string;
  activeTags: string[];
  allTags: string[];
}>();

const emit = defineEmits<{
  "update:search": [value: string];
  setTag: [tag: string | null];
  clearFilters: [];
}>();

const hasActiveFilters = computed(() => Boolean(props.search.trim() || props.activeTags.length));

const tagFilterLabel = computed(() => {
  if (props.activeTags.length === 0) return "all tags";
  if (props.activeTags.length === 1) return props.activeTags[0];
  return `${props.activeTags.length} tags`;
});
</script>

<template>
  <div class="mb-6 space-y-4">
    <div class="flex flex-wrap items-center justify-start gap-3">
      <AdminFilterDropdown
        v-if="allTags.length"
        :has-active-filters="hasActiveFilters"
        :active-label="tagFilterLabel"
        @clear="emit('clearFilters')"
      >
        <div class="flex flex-wrap justify-center gap-2">
          <button
            type="button"
            role="option"
            :aria-selected="activeTags.length === 0"
            :class="[
              'text-xs px-3 py-1 rounded-full border transition-colors',
              activeTags.length === 0
                ? 'border-accent-blue bg-accent-blue/15 text-accent-blue'
                : 'border-surface-border text-surface-mid hover:border-accent-blue/40 hover:text-surface-light',
            ]"
            @click="emit('setTag', null)"
          >
            all
          </button>
          <RecipeTagChip
            v-for="tag in allTags"
            :key="tag"
            role="option"
            :aria-selected="activeTags.includes(tag)"
            :tag="tag"
            :active="activeTags.includes(tag)"
            @click="emit('setTag', tag)"
          />
        </div>
      </AdminFilterDropdown>
      <BaseInput
        :model-value="search"
        type="search"
        compact
        placeholder="search recipe"
        aria-label="search recipe"
        @update:model-value="emit('update:search', String($event ?? ''))"
      />
    </div>
    <slot />
  </div>
</template>
