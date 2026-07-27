<script setup lang="ts">
import { computed } from "vue";

import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import { Card } from "@/components/ui/card";
import { CONTROL_SIZE } from "@/constants/formClasses";
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

const thumbInitials = computed(() => {
  const parts = props.recipe.title.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0] ?? ""}${parts[1][0] ?? ""}`.toUpperCase();
});

function onRowKeydown(event: KeyboardEvent): void {
  if (event.key !== "Enter" && event.key !== " ") return;
  event.preventDefault();
  emit("select", props.recipe.id);
}
</script>

<template>
  <Card
    as="div"
    interactive
    :hoverable="false"
    variant="ghost"
    role="button"
    tabindex="0"
    :class="[
      CONTROL_SIZE,
      'admin-list-row-rule group flex w-full min-w-0 cursor-pointer items-center overflow-hidden rounded-md !border-0 !bg-surface-card px-3 text-left ring-1 ring-inset ring-transparent hover:bg-surface-light/10 hover:ring-accent-blue/40 focus-visible:bg-surface-light/10 focus-visible:ring-accent-blue/40 focus-within:bg-surface-light/10 focus-within:ring-accent-blue/40',
    ]"
    :aria-label="`open recipe ${recipe.title}`"
    @click="emit('select', recipe.id)"
    @keydown="onRowKeydown"
  >
    <div class="flex h-full min-w-0 flex-1 items-center gap-2">
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

      <h3 class="min-w-0 flex-1 truncate text-sm font-semibold leading-none text-surface-light">
        {{ recipe.title }}
      </h3>

      <div
        v-if="canWrite"
        class="flex h-full shrink-0 items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-within:opacity-100 [@media(hover:none)]:opacity-100"
        @click.stop
        @keydown.stop
      >
        <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
      </div>
    </div>
  </Card>
</template>
