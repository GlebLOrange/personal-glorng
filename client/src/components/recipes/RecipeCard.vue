<script setup lang="ts">
import { computed } from "vue";

import ClockIcon from "@/components/icons/ClockIcon.vue";
import TagIcon from "@/components/icons/TagIcon.vue";
import UsersIcon from "@/components/icons/UsersIcon.vue";
import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import {
  ADMIN_ACTIONS_CLASS,
  ADMIN_TD_ACTIONS_CLASS,
  ADMIN_TD_CLASS,
  ADMIN_TH_ROW_CLASS,
  ADMIN_TR_CLASS,
} from "@/constants/adminDataTable";
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

const prepLabel = computed(() => formatRecipeTime(props.recipe.prep_time));
const cookLabel = computed(() => formatRecipeTime(props.recipe.cook_time));
const firstTag = computed(() => props.recipe.tags[0] ?? "");
const tagsTitle = computed(() => props.recipe.tags.join(", "));

const recipeMetaTitle = computed(() => {
  const parts: string[] = [];
  if (prepLabel.value) parts.push(`${prepLabel.value} prep`);
  if (cookLabel.value) parts.push(`${cookLabel.value} cook`);
  if (props.recipe.servings) parts.push(`${props.recipe.servings} servings`);
  if (props.recipe.tags.length) parts.push(tagsTitle.value);
  return parts.join(" · ");
});

const hasMeta = computed(() => Boolean(recipeMetaTitle.value));
</script>

<template>
  <tr
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
    <th :class="ADMIN_TH_ROW_CLASS" scope="row">
      <p class="truncate text-sm text-surface-light" :title="recipe.title">{{ recipe.title }}</p>
    </th>
    <td
      :class="[ADMIN_TD_CLASS, 'min-w-0 max-w-[14rem] overflow-hidden text-xs text-surface-mid']"
      :title="recipeMetaTitle || undefined"
    >
      <div v-if="hasMeta" class="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
        <span
          v-if="prepLabel"
          class="inline-flex min-w-0 items-center gap-1"
          :title="`${prepLabel} prep`"
          :aria-label="`${prepLabel} prep`"
        >
          <ClockIcon class-name="size-3.5 shrink-0" />
          <span class="truncate">{{ prepLabel }}</span>
        </span>
        <span
          v-if="cookLabel"
          class="inline-flex min-w-0 items-center gap-1"
          :title="`${cookLabel} cook`"
          :aria-label="`${cookLabel} cook`"
        >
          <ClockIcon class-name="size-3.5 shrink-0" />
          <span class="truncate">{{ cookLabel }}</span>
        </span>
        <span
          v-if="recipe.servings"
          class="inline-flex min-w-0 items-center gap-1"
          :aria-label="`${recipe.servings} servings`"
        >
          <UsersIcon class-name="size-3.5 shrink-0" />
          <span class="truncate">{{ recipe.servings }}</span>
        </span>
        <span
          v-if="firstTag"
          class="inline-flex min-w-0 max-w-full items-center gap-1"
          :title="tagsTitle"
        >
          <TagIcon class-name="size-3.5 shrink-0" />
          <span class="truncate">{{ firstTag }}</span>
        </span>
      </div>
      <template v-else>—</template>
    </td>
    <td :class="ADMIN_TD_ACTIONS_CLASS" @click.stop @keydown.stop>
      <div v-if="canWrite" :class="ADMIN_ACTIONS_CLASS">
        <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
      </div>
    </td>
  </tr>
</template>
