<script setup lang="ts">
import { computed } from "vue";

import ClockIcon from "@/components/icons/ClockIcon.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
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
    :title="recipe?.title ?? 'Loading recipe…'"
    max-width="lg"
    @close="emit('close')"
  >
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

      <div class="flex w-full flex-wrap items-center justify-between gap-2 text-xs">
        <span
          v-if="recipe.prep_time"
          class="inline-flex items-center gap-1 rounded-full border border-accent-blue/30 bg-accent-blue/15 px-2 py-1 text-accent-blue"
        >
          <ClockIcon class-name="size-3.5 shrink-0" />
          {{ formatRecipeTime(recipe.prep_time) }} prep
        </span>
        <span
          v-if="recipe.cook_time"
          class="inline-flex items-center gap-1 rounded-full border border-status-warning/30 bg-status-warning/15 px-2 py-1 text-status-warning"
        >
          <ClockIcon class-name="size-3.5 shrink-0" />
          {{ formatRecipeTime(recipe.cook_time) }} cook
        </span>
        <span
          v-if="recipe.servings"
          class="inline-flex items-center gap-1 rounded-full border border-status-success/30 bg-status-success/15 px-2 py-1 text-status-success"
        >
          <ClockIcon class-name="size-3.5 shrink-0" />
          {{ recipe.servings }} servings
        </span>
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
            <span class="text-accent-blue font-data shrink-0 w-5">{{ i + 1 }}.</span>
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
      <DrawerFooterActions>
        <template v-if="canWrite" #start>
          <IconCloseButton aria-label="delete recipe" @click="emit('delete')" />
          <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        </template>
        <template #primary>
          <ToolbarPillButton family="2xx" @click="emit('cook')">cook</ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
