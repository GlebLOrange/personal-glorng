<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
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
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        class="fixed inset-0 z-50 flex justify-end"
        @click.self="emit('close')"
      >
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="emit('close')" />
        <div
          class="relative w-full max-w-lg bg-surface-dark border-l border-surface-border overflow-y-auto p-6"
        >
          <div class="flex justify-between items-start mb-4">
            <h2 class="text-lg font-bold text-surface-light pr-4">
              {{ recipe?.title ?? "Loading recipe..." }}
            </h2>
            <button
              type="button"
              class="text-surface-mid hover:text-surface-light text-xl leading-none shrink-0"
              aria-label="Close"
              @click="emit('close')"
            >
              &times;
            </button>
          </div>

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
              <span
                v-for="tag in recipe.tags"
                :key="tag"
                class="text-[10px] px-2 py-0.5 rounded-full border border-accent-blue/40 text-accent-blue"
              >
                {{ tag }}
              </span>
            </div>

            <div>
              <h3 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-2">
                Ingredients
              </h3>
              <ul class="text-sm text-surface-light space-y-1">
                <li
                  v-for="(ing, i) in recipe.ingredients"
                  :key="i"
                  class="flex gap-2"
                >
                  <span class="text-accent-blue shrink-0">·</span>
                  <span>{{ ing }}</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-2">
                Steps
              </h3>
              <ol class="text-sm text-surface-light space-y-2">
                <li v-for="(step, i) in recipe.steps" :key="i" class="flex gap-2">
                  <span class="text-accent-blue font-mono shrink-0 w-5">{{ i + 1 }}.</span>
                  <span>{{ step }}</span>
                </li>
              </ol>
            </div>

            <div v-if="recipe.notes">
              <h3 class="text-xs font-bold text-surface-mid uppercase tracking-wider mb-2">
                Notes
              </h3>
              <p class="text-sm text-surface-light whitespace-pre-line">{{ recipe.notes }}</p>
            </div>

            <div class="flex flex-wrap gap-2 border-t border-surface-border pt-4">
              <BaseButton variant="primary" size="sm" @click="emit('cook')">Cook</BaseButton>
              <BaseButton
                v-if="canWrite"
                variant="ghost"
                size="sm"
                @click="emit('edit', recipe)"
              >
                Edit
              </BaseButton>
              <BaseButton
                v-if="canWrite"
                variant="ghost"
                size="sm"
                @click="emit('delete')"
              >
                Delete
              </BaseButton>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
