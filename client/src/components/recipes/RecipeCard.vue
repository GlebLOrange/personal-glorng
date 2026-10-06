<script setup lang="ts">
import { computed } from "vue";

import AdminListRow from "@/components/admin/AdminListRow.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import type { Recipe } from "@/types";
import { formatRecipeTime } from "@/utils/recipe";

const props = defineProps<{
  recipe: Recipe;
  canWrite?: boolean;
}>();

const emit = defineEmits<{
  select: [id: number];
  edit: [recipe: Recipe];
  delete: [recipe: Recipe];
}>();

const thumbInitials = computed(() => {
  const parts = props.recipe.title.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
});

const recipeMeta = computed(() => {
  const parts: string[] = [];
  const prep = formatRecipeTime(props.recipe.prep_time);
  if (prep) parts.push(`${prep} prep`);
  const cook = formatRecipeTime(props.recipe.cook_time);
  if (cook) parts.push(`${cook} cook`);
  if (props.recipe.servings) parts.push(`${props.recipe.servings} servings`);
  if (props.recipe.tags.length) {
    parts.push(props.recipe.tags.slice(0, 3).join(", "));
  }
  return parts.join(" · ");
});
</script>

<template>
  <AdminListRow
    interactive
    nested-interactive
    :open-label="`open recipe ${recipe.title}`"
    @click="emit('select', recipe.id)"
  >
    <template #leading>
      <BaseImage
        v-if="recipe.image_url"
        :src="recipe.image_url"
        :alt="recipe.title"
        class="size-6 shrink-0 rounded object-cover"
      />
      <div
        v-else
        class="flex size-6 shrink-0 items-center justify-center rounded bg-surface-dark text-[10px] font-semibold leading-none text-surface-sage"
        aria-hidden="true"
      >
        {{ thumbInitials }}
      </div>
    </template>

    <template #primary>
      <span :title="recipe.title">{{ recipe.title }}</span>
    </template>

    <template v-if="recipeMeta" #meta>
      <span :title="recipeMeta">{{ recipeMeta }}</span>
    </template>

    <template v-if="canWrite" #actions>
      <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
      <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
    </template>
  </AdminListRow>
</template>
