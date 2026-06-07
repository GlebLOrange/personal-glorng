<script setup lang="ts">
import { computed, onMounted, onUnmounted } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
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

function onKeydown(event: KeyboardEvent): void {
  if (event.key === "Escape") emit("close");
}

onMounted(() => document.addEventListener("keydown", onKeydown));
onUnmounted(() => document.removeEventListener("keydown", onKeydown));
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="fixed inset-0 z-50 flex justify-end">
      <Transition name="fade">
        <div
          v-if="open"
          class="absolute inset-0 bg-black/60 backdrop-blur-sm"
          @click="emit('close')"
        />
      </Transition>
      <Transition name="drawer-slide" appear>
        <div
          v-if="open"
          class="drawer-panel relative w-full max-w-lg h-full bg-surface-dark border-l border-surface-border flex flex-col"
          @click.stop
        >
          <header
            class="flex items-start justify-between gap-3 px-6 py-4 border-b border-surface-border shrink-0"
          >
            <h2 class="text-lg font-bold text-surface-light truncate min-w-0 flex-1">
              {{ recipe?.title ?? "Loading recipe..." }}
            </h2>
            <div class="flex items-center gap-1 shrink-0">
              <BaseDropdownMenu v-if="canWrite && recipe">
                <template #default="{ close: closeMenu }">
                  <BaseDropdownMenuItem
                    @select="
                      closeMenu();
                      emit('edit', recipe);
                    "
                  >
                    Edit
                  </BaseDropdownMenuItem>
                  <BaseDropdownMenuItem
                    destructive
                    @select="
                      closeMenu();
                      emit('delete');
                    "
                  >
                    Delete
                  </BaseDropdownMenuItem>
                </template>
              </BaseDropdownMenu>
              <button
                type="button"
                class="text-surface-mid hover:text-surface-light text-xl leading-none p-1 rounded focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
                aria-label="Close"
                @click="emit('close')"
              >
                &times;
              </button>
            </div>
          </header>

          <div class="flex-1 overflow-y-auto px-6 py-5">
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
                <h3 class="text-sm font-medium text-surface-mid mb-2">Ingredients</h3>
                <ul class="text-sm text-surface-light space-y-1">
                  <li v-for="(ing, i) in recipe.ingredients" :key="i" class="flex gap-2">
                    <span class="text-accent-blue shrink-0">·</span>
                    <span>{{ ing }}</span>
                  </li>
                </ul>
              </section>

              <section>
                <h3 class="text-sm font-medium text-surface-mid mb-2">Steps</h3>
                <ol class="text-sm text-surface-light space-y-2">
                  <li v-for="(step, i) in recipe.steps" :key="i" class="flex gap-2">
                    <span class="text-accent-blue font-mono shrink-0 w-5">{{ i + 1 }}.</span>
                    <span>{{ step }}</span>
                  </li>
                </ol>
              </section>

              <section v-if="recipe.notes">
                <h3 class="text-sm font-medium text-surface-mid mb-2">Notes</h3>
                <p class="text-sm text-surface-light whitespace-pre-line">{{ recipe.notes }}</p>
              </section>
            </div>
          </div>

          <footer
            v-if="recipe && !loading"
            class="shrink-0 px-6 py-4 border-t border-surface-border bg-surface-dark"
          >
            <BaseButton variant="primary" class="w-full" @click="emit('cook')"> Cook </BaseButton>
          </footer>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>
