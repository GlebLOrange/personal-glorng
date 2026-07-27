<script setup lang="ts">
import { ref } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { newsStatusClass } from "@/constants/filterColors";
import {
  NEWS_STATUSES,
  NEWS_TAG_LIMIT,
  NEWS_TAGS,
  newsStatusDescription,
  newsStatusLabel,
} from "@/constants/news";
import type { NewsArticleFormData, NewsStatus } from "@/types";

const form = defineModel<NewsArticleFormData>({ required: true });

const props = defineProps<{
  canWrite: boolean;
}>();

const tagsOpen = ref(false);

function parsedTags(): string[] {
  return form.value.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

function tagIsSelected(tag: string): boolean {
  return parsedTags().includes(tag);
}

function selectedTagsLabel(): string {
  const tags = parsedTags();
  return tags.length > 0 ? tags.join(", ") : "none";
}

function setStatus(status: NewsStatus): void {
  if (!props.canWrite) return;
  form.value.status = status;
}

function toggleTag(tag: string): void {
  if (!props.canWrite) return;
  const tags = parsedTags();
  if (tags.includes(tag)) {
    form.value.tags = tags.filter((item) => item !== tag).join(", ");
    return;
  }
  if (tags.length >= NEWS_TAG_LIMIT) return;
  form.value.tags = [...tags, tag].join(", ");
}

function onTagsToggle(event: Event): void {
  tagsOpen.value = (event.target as HTMLDetailsElement).open;
}
</script>

<template>
  <Card>
    <h2 class="card-title mb-4">article</h2>
    <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
      <BaseInput
        v-model="form.slug"
        placeholder="slug"
        aria-label="slug"
        :disabled="!canWrite"
      />
      <div
        class="grid grid-cols-2 gap-2 sm:col-span-2 sm:grid-cols-3"
        role="group"
        aria-label="status"
      >
        <AdminFilterChip
          v-for="status in NEWS_STATUSES"
          :key="status"
          :label="newsStatusLabel(status)"
          :title="newsStatusDescription(status)"
          align="center"
          :active="form.status === status"
          :color-class="newsStatusClass(status)"
          :disabled="!canWrite"
          @click="setStatus(status)"
        />
      </div>
      <BaseInput
        v-model="form.title"
        placeholder="title"
        aria-label="title"
        :disabled="!canWrite"
      />
      <BaseInput
        v-model="form.original_title"
        placeholder="original title"
        aria-label="original title"
        :disabled="!canWrite"
      />
      <BaseInput
        v-model="form.language"
        placeholder="language (en)"
        aria-label="language"
        :disabled="!canWrite"
      />
    </div>
    <details
      class="mt-4 rounded border border-surface-border px-3 py-2"
      @toggle="onTagsToggle"
    >
      <summary
        class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
      >
        <ChevronIcon :open="tagsOpen" />
        tags ({{ parsedTags().length }}/{{ NEWS_TAG_LIMIT }})
        <span class="text-xs text-surface-muted"> — {{ selectedTagsLabel() }}</span>
      </summary>
      <div class="mt-3 flex flex-wrap gap-2">
        <label
          v-for="tag in NEWS_TAGS"
          :key="tag"
          :for="`news-edit-tag-${tag}`"
          class="inline-flex cursor-pointer items-center rounded px-2.5 py-1 text-xs lowercase transition-colors"
          :class="{
            'bg-accent-blue/10 text-accent-blue': tagIsSelected(tag),
            'text-surface-mid hover:bg-surface-mid/10': !tagIsSelected(tag),
            'opacity-50': !tagIsSelected(tag) && parsedTags().length >= NEWS_TAG_LIMIT,
          }"
        >
          <input
            :id="`news-edit-tag-${tag}`"
            type="checkbox"
            class="sr-only"
            :checked="tagIsSelected(tag)"
            :disabled="
              !canWrite || (!tagIsSelected(tag) && parsedTags().length >= NEWS_TAG_LIMIT)
            "
            @change="toggleTag(tag)"
          />
          {{ tag }}
        </label>
      </div>
    </details>
    <div class="mt-4">
      <BaseTextarea
        v-model="form.summary"
        :rows="4"
        placeholder="summary"
        aria-label="summary"
        :disabled="!canWrite"
      />
    </div>
  </Card>
</template>
