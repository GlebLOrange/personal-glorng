<script setup lang="ts">
import { computed } from "vue";

import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_MOBILE_ROW_WRAP_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TD_MUTED_CLASS,
  ADMIN_TD_TITLE_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
import type { Recipe } from "@/types";
import { formatRecipeTime } from "@/utils/recipe";

const props = withDefaults(
  defineProps<{
    recipe: Recipe;
    canWrite?: boolean;
    layout?: "card" | "table";
  }>(),
  { layout: "card" },
);

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
  <tr
    v-if="layout === 'table'"
    :class="[ADMIN_TR_CLASS, 'cursor-pointer']"
    role="button"
    tabindex="0"
    :aria-label="`open recipe ${recipe.title}`"
    @click="emit('select', recipe.id)"
    @keydown.enter.prevent="emit('select', recipe.id)"
    @keydown.space.prevent="emit('select', recipe.id)"
  >
    <td :class="ADMIN_TD_CLASS">
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
    </td>
    <td :class="ADMIN_TD_TITLE_CLASS">
      <p class="truncate text-sm text-surface-light" :title="recipe.title">{{ recipe.title }}</p>
    </td>
    <td :class="ADMIN_TD_MUTED_CLASS" :title="recipeMeta || undefined">
      {{ recipeMeta || "—" }}
    </td>
    <td :class="ADMIN_TD_ACTIONS_CLASS" @click.stop @keydown.stop>
      <div v-if="canWrite" :class="ADMIN_ACTIONS_CLASS">
        <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
      </div>
    </td>
  </tr>

  <div
    v-else
    :class="[ADMIN_MOBILE_ROW_WRAP_CLASS, 'flex min-w-0 cursor-pointer items-center gap-2']"
    role="button"
    tabindex="0"
    :aria-label="`open recipe ${recipe.title}`"
    @click="emit('select', recipe.id)"
    @keydown.enter.prevent="emit('select', recipe.id)"
    @keydown.space.prevent="emit('select', recipe.id)"
  >
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
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm text-surface-light" :title="recipe.title">{{ recipe.title }}</p>
      <p v-if="recipeMeta" class="mt-0.5 truncate text-xs text-surface-mid" :title="recipeMeta">
        {{ recipeMeta }}
      </p>
    </div>
    <div v-if="canWrite" :class="ADMIN_ACTIONS_CLASS" @click.stop @keydown.stop>
      <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
      <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
    </div>
  </div>
</template>
