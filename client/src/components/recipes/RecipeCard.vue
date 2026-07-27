<script setup lang="ts">
import { computed } from "vue";

import BaseImage from "@/components/ui/BaseImage.vue";
import IconCloseButton from "@/components/ui/IconCloseButton.vue";
import IconEditButton from "@/components/ui/IconEditButton.vue";
import { Card } from "@/components/ui/card";
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
    hoverable
    variant="dense"
    role="button"
    tabindex="0"
    class="group w-full min-w-0 cursor-pointer text-left"
    :aria-label="`Open recipe ${recipe.title}`"
    @click="emit('select', recipe.id)"
    @keydown="onRowKeydown"
  >
    <div class="flex min-w-0 items-center gap-2">
      <BaseImage
        v-if="recipe.image_url"
        :src="recipe.image_url"
        :alt="recipe.title"
        class="size-7 shrink-0 rounded object-cover"
      />
      <div
        v-else
        class="flex size-7 shrink-0 items-center justify-center rounded bg-surface-dark text-[10px] font-semibold leading-none text-surface-sage"
        aria-hidden="true"
      >
        {{ thumbInitials }}
      </div>

      <h3 class="min-w-0 flex-1 truncate text-sm font-semibold leading-none text-surface-light">
        {{ recipe.title }}
      </h3>

      <div
        v-if="canWrite"
        class="flex shrink-0 items-center gap-0.5 opacity-0 transition-opacity group-hover:opacity-100 group-focus-within:opacity-100 focus-within:opacity-100 [@media(hover:none)]:opacity-100"
        @click.stop
        @keydown.stop
      >
        <IconEditButton aria-label="edit recipe" @click="emit('edit', recipe)" />
        <IconCloseButton aria-label="delete recipe" @click="emit('delete', recipe)" />
      </div>
    </div>
  </Card>
</template>
