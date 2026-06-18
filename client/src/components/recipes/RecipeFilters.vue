<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import type { RecipeSort } from "@/types";

const props = defineProps<{
  search: string;
  activeTags: string[];
  sort: RecipeSort;
  allTags: string[];
  recipeCountLabel: string;
  canWrite?: boolean;
}>();

const emit = defineEmits<{
  "update:search": [value: string];
  "update:sort": [value: RecipeSort];
  setTag: [tag: string | null];
  create: [];
  clearFilters: [];
}>();

const hasActiveFilters = computed(() => Boolean(props.search.trim() || props.activeTags.length));

const sortOptions: { value: RecipeSort; label: string }[] = [
  { value: "updated_desc", label: "Recently updated" },
  { value: "title_asc", label: "Title A–Z" },
  { value: "title_desc", label: "Title Z–A" },
  { value: "prep_asc", label: "Shortest prep" },
  { value: "total_time_asc", label: "Shortest total time" },
];
</script>

<template>
  <div class="space-y-4 mb-6">
    <BaseInput
      :model-value="search"
      placeholder="Search recipes..."
      @update:model-value="emit('update:search', String($event ?? ''))"
    />

    <div class="grid grid-cols-1 lg:grid-cols-[14rem_minmax(0,1fr)] gap-4 lg:gap-6">
      <aside
        class="rounded-lg border border-surface-border bg-surface-card p-4 space-y-5 lg:sticky lg:top-24 lg:self-start"
      >
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-semibold text-surface-light">Filter recipes</h2>
            <p class="text-xs text-surface-mid mt-1">{{ recipeCountLabel }}</p>
          </div>
          <BaseButton v-if="canWrite" variant="primary" size="sm" @click="emit('create')">
            + Add
          </BaseButton>
        </div>

        <div class="space-y-2">
          <label
            for="recipe-sort"
            class="text-xs font-semibold uppercase tracking-wide text-surface-mid"
          >
            Sort
          </label>
          <select
            id="recipe-sort"
            :value="sort"
            class="w-full bg-surface-dark border border-surface-border rounded-lg px-3 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors"
            @change="emit('update:sort', ($event.target as HTMLSelectElement).value as RecipeSort)"
          >
            <option v-for="option in sortOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <div v-if="allTags.length" class="space-y-2">
          <p class="text-xs font-semibold uppercase tracking-wide text-surface-mid">Tags</p>
          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              :class="[
                'text-xs px-3 py-1 rounded-full border transition-colors',
                activeTags.length === 0
                  ? 'border-accent-blue bg-accent-blue/15 text-accent-blue'
                  : 'border-surface-border text-surface-mid hover:border-accent-blue/40 hover:text-surface-light',
              ]"
              @click="emit('setTag', null)"
            >
              All
            </button>
            <RecipeTagChip
              v-for="tag in allTags"
              :key="tag"
              :tag="tag"
              :active="activeTags.includes(tag)"
              @click="emit('setTag', tag)"
            />
          </div>
        </div>

        <BaseButton v-if="hasActiveFilters" variant="ghost" size="sm" @click="emit('clearFilters')">
          Clear filters
        </BaseButton>
      </aside>

      <div class="min-w-0">
        <slot />
      </div>
    </div>
  </div>
</template>
