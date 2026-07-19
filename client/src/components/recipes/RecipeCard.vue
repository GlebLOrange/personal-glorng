<script setup lang="ts">
import { Card } from "@/components/ui/card";
import BaseImage from "@/components/ui/BaseImage.vue";
import { formatRecipeTime } from "@/utils/recipe";
import type { Recipe } from "@/types";

defineProps<{
  recipe: Recipe;
}>();

const emit = defineEmits<{
  select: [id: number];
}>();
</script>

<template>
  <Card hoverable class="flex flex-col">
    <button
      type="button"
      class="text-left w-full rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
      :aria-label="`Open recipe ${recipe.title}`"
      @click="emit('select', recipe.id)"
    >
      <BaseImage
        :src="recipe.image_url"
        :alt="recipe.title"
        class="w-full h-40 rounded-md mb-3 -mt-1 object-cover"
      />

      <h3 class="text-surface-light font-bold text-sm mb-2 line-clamp-2">{{ recipe.title }}</h3>

      <div class="flex flex-wrap gap-x-3 gap-y-1 text-xs text-surface-mid">
        <span v-if="recipe.prep_time">{{ formatRecipeTime(recipe.prep_time) }} prep</span>
        <span v-if="recipe.cook_time">{{ formatRecipeTime(recipe.cook_time) }} cook</span>
        <span v-if="recipe.servings">{{ recipe.servings }} servings</span>
      </div>
    </button>
  </Card>
</template>
