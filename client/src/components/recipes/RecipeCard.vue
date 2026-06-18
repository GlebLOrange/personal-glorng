<script setup lang="ts">
import BaseCard from "@/components/ui/BaseCard.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import { formatRecipeTime } from "@/utils/recipe";
import type { Recipe } from "@/types";

defineProps<{
  recipe: Recipe;
  activeTags: string[];
}>();

const emit = defineEmits<{
  select: [id: number];
  tagClick: [tag: string];
}>();
</script>

<template>
  <BaseCard hoverable class="cursor-pointer flex flex-col" @click="emit('select', recipe.id)">
    <BaseImage
      :src="recipe.image_url"
      :alt="recipe.title"
      class="w-full h-40 rounded-md mb-3 -mt-1 object-cover"
    />

    <h3 class="text-surface-light font-bold text-sm mb-2 line-clamp-2">{{ recipe.title }}</h3>

    <div v-if="recipe.tags.length" class="flex flex-wrap gap-1.5 mb-3">
      <RecipeTagChip
        v-for="tag in recipe.tags"
        :key="tag"
        :tag="tag"
        :active="activeTags.includes(tag)"
        compact
        @click.stop="emit('tagClick', tag)"
      />
    </div>

    <div class="flex flex-wrap gap-x-3 gap-y-1 text-xs text-surface-mid mt-auto">
      <span v-if="recipe.prep_time">{{ formatRecipeTime(recipe.prep_time) }} prep</span>
      <span v-if="recipe.cook_time">{{ formatRecipeTime(recipe.cook_time) }} cook</span>
      <span v-if="recipe.servings">{{ recipe.servings }} servings</span>
    </div>
  </BaseCard>
</template>
