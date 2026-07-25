<script setup lang="ts">
import { computed } from "vue";

import ClockIcon from "@/components/icons/ClockIcon.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import { Card } from "@/components/ui/card";
import { formatRecipeTime } from "@/utils/recipe";
import type { Recipe } from "@/types";

const props = defineProps<{
  recipe: Recipe;
  canWrite?: boolean;
}>();

const emit = defineEmits<{
  select: [id: number];
  edit: [recipe: Recipe];
  delete: [recipe: Recipe];
}>();

const prepLabel = computed(() => formatRecipeTime(props.recipe.prep_time));
const cookLabel = computed(() => formatRecipeTime(props.recipe.cook_time));
const hasMeta = computed(() =>
  Boolean(prepLabel.value || cookLabel.value || props.recipe.servings),
);

const thumbInitials = computed(() => {
  const parts = props.recipe.title.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
});
</script>

<template>
  <Card
    as="div"
    variant="ghost"
    class="group w-full min-w-0 rounded-lg px-2 py-1.5 text-left hover:bg-surface-light/5"
  >
    <div class="flex min-w-0 items-center gap-2">
      <button
        type="button"
        class="flex min-w-0 flex-1 cursor-pointer items-center gap-2 rounded text-left focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
        :aria-label="`Open recipe ${recipe.title}`"
        @click="emit('select', recipe.id)"
      >
        <BaseImage
          v-if="recipe.image_url"
          :src="recipe.image_url"
          :alt="recipe.title"
          class="size-10 shrink-0 rounded-md object-cover"
        />
        <div
          v-else
          class="flex size-10 shrink-0 items-center justify-center rounded-md bg-surface-dark text-xs font-semibold text-surface-sage"
          aria-hidden="true"
        >
          {{ thumbInitials }}
        </div>

        <div class="flex min-w-0 flex-1 items-center gap-2">
          <h3 class="min-w-0 flex-1 truncate text-sm font-bold text-surface-light">
            {{ recipe.title }}
          </h3>
          <div v-if="hasMeta" class="flex shrink-0 flex-wrap items-center justify-end gap-1">
            <span
              v-if="prepLabel"
              class="inline-flex items-center gap-0.5 rounded-full border border-accent-blue/30 bg-accent-blue/15 px-1.5 py-0.5 text-[10px] text-accent-blue"
            >
              <ClockIcon class-name="size-3 shrink-0" />
              prep {{ prepLabel }}
            </span>
            <span
              v-if="cookLabel"
              class="inline-flex items-center gap-0.5 rounded-full border border-status-cyan/30 bg-status-cyan/15 px-1.5 py-0.5 text-[10px] text-status-cyan"
            >
              <ClockIcon class-name="size-3 shrink-0" />
              cook {{ cookLabel }}
            </span>
            <span
              v-if="recipe.servings"
              class="inline-flex items-center gap-0.5 rounded-full border border-status-success/30 bg-status-success/15 px-1.5 py-0.5 text-[10px] text-status-success"
            >
              <ClockIcon class-name="size-3 shrink-0" />
              {{ recipe.servings }} servings
            </span>
          </div>
        </div>
      </button>

      <div
        v-if="canWrite"
        class="flex shrink-0 items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-within:opacity-100 [@media(hover:none)]:opacity-100"
      >
        <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
      </div>
    </div>
  </Card>
</template>
