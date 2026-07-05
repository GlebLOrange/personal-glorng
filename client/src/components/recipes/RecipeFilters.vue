<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useTemplateRef } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import { Card } from "@/components/ui/card";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import type { RecipeSort } from "@/types";

const props = defineProps<{
  search: string;
  activeTags: string[];
  sort: RecipeSort;
  allTags: string[];
  recipeCountLabel: string;
}>();

const emit = defineEmits<{
  "update:search": [value: string];
  "update:sort": [value: RecipeSort];
  setTag: [tag: string | null];
  clearFilters: [];
}>();

const hasActiveFilters = computed(() => Boolean(props.search.trim() || props.activeTags.length));
const tagMenuOpen = ref(false);
const tagMenuRef = useTemplateRef<HTMLElement>("tagMenu");

const tagFilterLabel = computed(() => {
  if (props.activeTags.length === 0) return "All tags";
  if (props.activeTags.length === 1) return props.activeTags[0];
  return `${props.activeTags.length} tags`;
});

const sortOptions: { value: RecipeSort; label: string }[] = [
  { value: "updated_desc", label: "Recently updated" },
  { value: "title_asc", label: "Title A–Z" },
  { value: "title_desc", label: "Title Z–A" },
  { value: "prep_asc", label: "Shortest prep" },
  { value: "total_time_asc", label: "Shortest total time" },
];

function closeTagMenu(): void {
  tagMenuOpen.value = false;
}

function toggleTagMenu(): void {
  tagMenuOpen.value = !tagMenuOpen.value;
}

function onDocumentClick(event: MouseEvent): void {
  const root = tagMenuRef.value;
  if (tagMenuOpen.value && root && !root.contains(event.target as Node)) closeTagMenu();
}

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape" && tagMenuOpen.value) {
    event.stopPropagation();
    closeTagMenu();
  }
}

onMounted(() => {
  document.addEventListener("click", onDocumentClick);
  document.addEventListener("keydown", onKeydown);
});

onUnmounted(() => {
  document.removeEventListener("click", onDocumentClick);
  document.removeEventListener("keydown", onKeydown);
});
</script>

<template>
  <div class="space-y-4 mb-6">
    <BaseInput
      :model-value="search"
      placeholder="Search recipes..."
      @update:model-value="emit('update:search', String($event ?? ''))"
    />

    <div class="space-y-4">
      <Card variant="compact" class="flex flex-wrap items-center gap-3 !p-3">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-sm font-semibold text-surface-light">Filter recipes</h2>
            <p class="text-xs text-surface-mid mt-1">{{ recipeCountLabel }}</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <label
            for="recipe-sort"
            class="text-xs font-semibold uppercase tracking-wide text-surface-mid"
          >
            Sort
          </label>
          <select
            id="recipe-sort"
            :value="sort"
            class="h-[34px] min-w-[12rem] bg-surface-dark border border-surface-border rounded-lg px-2 py-1.5 text-surface-light text-xs focus:outline-none focus:border-accent-blue transition-colors"
            @change="emit('update:sort', ($event.target as HTMLSelectElement).value as RecipeSort)"
          >
            <option v-for="option in sortOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>

        <div v-if="allTags.length" ref="tagMenu" class="relative">
          <button
            type="button"
            class="inline-flex h-[34px] min-w-[8rem] items-center justify-between gap-2 rounded-lg border border-surface-border bg-surface-dark px-3 py-1.5 text-xs text-surface-light transition-colors hover:border-accent-blue/40 focus:outline-none focus:border-accent-blue"
            aria-haspopup="listbox"
            :aria-expanded="tagMenuOpen"
            @click.stop="toggleTagMenu"
          >
            <span class="truncate">{{ tagFilterLabel }}</span>
            <span class="text-surface-mid" aria-hidden="true">▾</span>
          </button>

          <Card
            v-if="tagMenuOpen"
            role="listbox"
            aria-label="Filter by tags"
            aria-multiselectable="true"
            variant="compact"
            class="absolute right-0 top-full z-10 mt-2 max-h-64 w-max max-w-[min(20rem,calc(100vw-2rem))] overflow-y-auto !p-3 shadow-lg"
            @click.stop
          >
            <div class="flex flex-wrap gap-2">
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
                All
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
          </Card>
        </div>

        <BaseButton v-if="hasActiveFilters" variant="ghost" size="sm" @click="emit('clearFilters')">
          Clear filters
        </BaseButton>
      </Card>

      <slot />
    </div>
  </div>
</template>
