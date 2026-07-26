<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";

import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import { RECIPE_TAG_LIMIT, RECIPE_TAG_SET, RECIPE_TAGS } from "@/constants/recipes";

const props = defineProps<{
  tags: string;
  /** Drawer open flag — resets details open state when the form opens. */
  formOpen: boolean;
}>();

const emit = defineEmits<{
  "update:tags": [value: string];
}>();

const selectedTags = computed(() =>
  props.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean),
);

/** Catalog tags plus any selected custom/imported tags not in the curated list. */
const tagChoices = computed(() => {
  const extras = selectedTags.value.filter((tag) => !RECIPE_TAG_SET.has(tag));
  return [...RECIPE_TAGS, ...extras];
});

// Uncontrolled <details>; set .open on drawer open so Vue doesn't fight native toggles.
const detailsRef = ref<HTMLDetailsElement | null>(null);

watch(
  () => props.formOpen,
  async (isOpen) => {
    if (!isOpen) return;
    await nextTick();
    if (detailsRef.value) detailsRef.value.open = false;
  },
);

function tagIsSelected(tag: string): boolean {
  return selectedTags.value.includes(tag);
}

function toggleTag(tag: string): void {
  const tags = selectedTags.value;
  if (tags.includes(tag)) {
    emit("update:tags", tags.filter((item) => item !== tag).join(", "));
    return;
  }
  if (tags.length >= RECIPE_TAG_LIMIT) return;
  emit("update:tags", [...tags, tag].join(", "));
}
</script>

<template>
  <details ref="detailsRef" class="group rounded border border-surface-border">
    <summary
      class="flex h-8 cursor-pointer list-none items-center gap-1.5 px-2 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
    >
      <ChevronIcon class-name="size-3.5 group-open:rotate-180" />
      tags ({{ selectedTags.length }}/{{ RECIPE_TAG_LIMIT }})
    </summary>
    <div class="flex flex-wrap gap-1.5 border-t border-surface-border px-2 py-2">
      <button
        v-for="tag in tagChoices"
        :key="tag"
        type="button"
        class="inline-flex items-center rounded border px-2 py-1 text-xs transition-colors"
        :class="{
          'border-transparent bg-accent-blue/15 text-accent-blue': tagIsSelected(tag),
          'border-transparent text-surface-mid hover:border-surface-border/50':
            !tagIsSelected(tag),
          'opacity-50': !tagIsSelected(tag) && selectedTags.length >= RECIPE_TAG_LIMIT,
        }"
        :aria-pressed="tagIsSelected(tag)"
        :disabled="!tagIsSelected(tag) && selectedTags.length >= RECIPE_TAG_LIMIT"
        @click="toggleTag(tag)"
      >
        {{ tag }}
      </button>
    </div>
  </details>
</template>
