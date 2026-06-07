<script setup lang="ts">
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import type { RecipeSort } from "@/types";

defineProps<{
  search: string;
  activeTag: string | null;
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
}>();

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
    <div class="flex flex-col sm:flex-row gap-3">
      <div class="flex-1">
        <BaseInput
          :model-value="search"
          placeholder="Search recipes..."
          @update:model-value="emit('update:search', String($event ?? ''))"
        />
      </div>
      <div class="flex gap-2 items-end">
        <select
          :value="sort"
          class="bg-surface-dark border border-surface-border rounded-lg px-4 py-2 text-surface-light text-sm focus:outline-none focus:border-accent-blue transition-colors h-[42px]"
          @change="emit('update:sort', ($event.target as HTMLSelectElement).value as RecipeSort)"
        >
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
        <BaseButton v-if="canWrite" variant="primary" @click="emit('create')">+ Add</BaseButton>
      </div>
    </div>

    <div v-if="allTags.length" class="flex gap-2 overflow-x-auto pb-1 -mx-1 px-1">
      <button
        type="button"
        :class="[
          'shrink-0 text-xs px-3 py-1 rounded-full border transition-colors',
          activeTag === null
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
        :active="activeTag === tag"
        @click="emit('setTag', tag)"
      />
    </div>

    <p class="text-xs text-surface-mid">{{ recipeCountLabel }}</p>
  </div>
</template>
