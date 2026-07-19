<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseDropdownMenu from "@/components/ui/BaseDropdownMenu.vue";
import BaseDropdownMenuItem from "@/components/ui/BaseDropdownMenuItem.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import RecipeTagChip from "@/components/recipes/RecipeTagChip.vue";
import { usePermissions } from "@/composables/usePermissions";
import { formatRecipeTime } from "@/utils/recipe";
import type { Recipe } from "@/types";

defineProps<{
  open: boolean;
  recipe: Recipe | null;
  loading: boolean;
}>();

const { can } = usePermissions();
const canWrite = computed(() => can("recipes", "write"));

const emit = defineEmits<{
  close: [];
  edit: [recipe: Recipe];
  delete: [];
  cook: [];
}>();
</script>

<template>
  <BaseDrawer
    :open="open"
    :title="recipe?.title ?? 'Loading recipe...'"
    max-width="lg"
    @close="emit('close')"
  >
    <template v-if="canWrite && recipe" #header-actions>
      <BaseDropdownMenu aria-label="Recipe actions">
        <template #default="{ close: closeMenu }">
          <BaseDropdownMenuItem
            @select="
              closeMenu();
              emit('edit', recipe);
            "
          >
            edit
          </BaseDropdownMenuItem>
          <BaseDropdownMenuItem
            destructive
            @select="
              closeMenu();
              emit('delete');
            "
          >
            delete
          </BaseDropdownMenuItem>
        </template>
      </BaseDropdownMenu>
    </template>

    <div v-if="loading || !recipe" class="space-y-3 animate-pulse">
      <div class="h-40 bg-surface-border rounded-md" />
      <div class="h-4 w-full bg-surface-border rounded" />
      <div class="h-4 w-3/4 bg-surface-border rounded" />
    </div>

    <div v-else class="space-y-5">
      <BaseImage
        :src="recipe.image_url"
        :alt="recipe.title"
        class="w-full h-48 rounded-md object-cover"
      />

      <div class="flex flex-wrap gap-2 text-xs text-surface-mid">
        <span
          v-if="recipe.prep_time"
          class="px-2 py-1 rounded-full border border-surface-border"
        >
          {{ formatRecipeTime(recipe.prep_time) }} prep
        </span>
        <span
          v-if="recipe.cook_time"
          class="px-2 py-1 rounded-full border border-surface-border"
        >
          {{ formatRecipeTime(recipe.cook_time) }} cook
        </span>
        <span
          v-if="recipe.servings"
          class="px-2 py-1 rounded-full border border-surface-border"
        >
          {{ recipe.servings }} servings
        </span>
      </div>

      <div v-if="recipe.tags.length" class="flex flex-wrap gap-1.5">
        <RecipeTagChip v-for="tag in recipe.tags" :key="tag" :tag="tag" compact />
      </div>

      <section>
        <h3 class="text-sm font-medium text-surface-mid mb-2">ingredients</h3>
        <ul class="text-sm text-surface-light space-y-1">
          <li v-for="(ing, i) in recipe.ingredients" :key="i" class="flex gap-2">
            <span class="text-accent-blue shrink-0">·</span>
            <span>{{ ing }}</span>
          </li>
        </ul>
      </section>

      <section>
        <h3 class="text-sm font-medium text-surface-mid mb-2">steps</h3>
        <ol class="text-sm text-surface-light space-y-2">
          <li v-for="(step, i) in recipe.steps" :key="i" class="flex gap-2">
            <span class="text-accent-blue font-mono shrink-0 w-5">{{ i + 1 }}.</span>
            <span>{{ step }}</span>
          </li>
        </ol>
      </section>

      <section v-if="recipe.notes">
        <h3 class="text-sm font-medium text-surface-mid mb-2">notes</h3>
        <p class="text-sm text-surface-light whitespace-pre-line">{{ recipe.notes }}</p>
      </section>
    </div>

    <template v-if="recipe && !loading" #footer>
      <BaseButton variant="primary" class="w-full" @click="emit('cook')">cook</BaseButton>
    </template>
  </BaseDrawer>
</template>
