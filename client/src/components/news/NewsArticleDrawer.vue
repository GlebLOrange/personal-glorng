<script setup lang="ts">
import { computed, ref, watch } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { newsStatusClass } from "@/constants/filterColors";
import { SELECT_CLASS } from "@/constants/formClasses";
import { NEWS_STATUSES, NEWS_TAG_LIMIT, NEWS_TAGS } from "@/constants/news";
import type { NewsArticleFormData, NewsSource, NewsStatus } from "@/types";

const props = defineProps<{
  open: boolean;
  mode: "create" | "edit";
  form: NewsArticleFormData;
  sources: NewsSource[];
  loading: boolean;
}>();

const emit = defineEmits<{
  close: [];
  delete: [];
  save: [];
  "update:form": [value: NewsArticleFormData];
}>();

const tagsOpen = ref(false);

const title = computed(() => (props.mode === "create" ? "new article" : "edit article"));
const selectedTags = computed(() =>
  props.form.tags
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean),
);
const selectedTagsLabel = computed(() =>
  selectedTags.value.length > 0 ? selectedTags.value.join(", ") : "none",
);

watch(
  () => props.open,
  (isOpen) => {
    if (!isOpen) tagsOpen.value = false;
  },
);

function patch(patchValue: Partial<NewsArticleFormData>): void {
  emit("update:form", { ...props.form, ...patchValue });
}

function toStringValue(value: string | number | null | undefined): string {
  return String(value ?? "");
}

function toSourceId(value: string): number | null {
  const sourceId = Number(value);
  return Number.isInteger(sourceId) && sourceId > 0 ? sourceId : null;
}

function setStatus(status: NewsStatus): void {
  patch({ status });
}

function tagIsSelected(tag: string): boolean {
  return selectedTags.value.includes(tag);
}

function toggleTag(tag: string): void {
  const tags = selectedTags.value;
  if (tags.includes(tag)) {
    patch({ tags: tags.filter((item) => item !== tag).join(", ") });
    return;
  }
  if (tags.length >= NEWS_TAG_LIMIT) return;
  patch({ tags: [...tags, tag].join(", ") });
}

function onTagsToggle(event: Event): void {
  tagsOpen.value = (event.target as HTMLDetailsElement).open;
}
</script>

<template>
  <BaseDrawer
    :open="open"
    :title="title"
    max-width="2xl"
    :header-class="newsStatusClass(form.status)"
    @close="emit('close')"
  >
    <form class="space-y-6" @submit.prevent="emit('save')">
      <section class="space-y-4">
        <select
          :value="form.source_id ?? ''"
          aria-label="source"
          :class="SELECT_CLASS"
          @change="patch({ source_id: toSourceId(($event.target as HTMLSelectElement).value) })"
        >
          <option value="">auto from URL host</option>
          <option v-for="source in sources" :key="source.id" :value="source.id">
            {{ source.name }}{{ source.host ? ` (${source.host})` : "" }}
          </option>
        </select>
        <BaseInput
          :model-value="form.source_url"
          placeholder="article url (example.com or https://…)"
          aria-label="article url (example.com or https://…)"
          type="url"
          @update:model-value="patch({ source_url: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_name"
          placeholder="source name (e.g. DW)"
          @update:model-value="patch({ source_name: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_feed_url"
          placeholder="source feed/home url (example.com or https://…)"
          aria-label="source feed/home url (example.com or https://…)"
          type="url"
          @update:model-value="patch({ source_feed_url: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_published_at"
          type="datetime-local"
          aria-label="source published at"
          @update:model-value="patch({ source_published_at: toStringValue($event) })"
        />
        <div class="grid grid-cols-2 gap-2 sm:grid-cols-4" role="group" aria-label="status">
          <AdminFilterChip
            v-for="status in NEWS_STATUSES"
            :key="status"
            :label="status"
            align="center"
            :active="form.status === status"
            :color-class="newsStatusClass(status)"
            @click="setStatus(status)"
          />
        </div>
      </section>

      <section class="space-y-4">
        <h3 class="text-sm font-medium text-surface-mid">article</h3>
        <BaseInput
          v-if="mode === 'edit'"
          :model-value="form.slug"
          placeholder="slug (article-url-slug)"
          @update:model-value="patch({ slug: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.title"
          placeholder="title"
          @update:model-value="patch({ title: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.original_title"
          placeholder="original title"
          @update:model-value="patch({ original_title: toStringValue($event) })"
        />
        <BaseTextarea
          :model-value="form.summary"
          :rows="4"
          placeholder="summary"
          @update:model-value="patch({ summary: toStringValue($event) })"
        />
        <details class="rounded border border-surface-border px-3 py-2" @toggle="onTagsToggle">
          <summary
            class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
          >
            <ChevronIcon :open="tagsOpen" />
            tags ({{ selectedTags.length }}/{{ NEWS_TAG_LIMIT }})
            <span class="text-xs text-surface-muted"> — {{ selectedTagsLabel }}</span>
          </summary>
          <div class="mt-3 flex flex-wrap gap-2">
            <label
              v-for="tag in NEWS_TAGS"
              :key="tag"
              :for="`news-drawer-tag-${tag}`"
              class="inline-flex cursor-pointer items-center rounded px-2.5 py-1 text-xs lowercase transition-colors"
              :class="{
                'bg-accent-blue/10 text-accent-blue': tagIsSelected(tag),
                'text-surface-mid hover:bg-surface-mid/10': !tagIsSelected(tag),
                'opacity-50': !tagIsSelected(tag) && selectedTags.length >= NEWS_TAG_LIMIT,
              }"
            >
              <input
                :id="`news-drawer-tag-${tag}`"
                type="checkbox"
                class="sr-only"
                :checked="tagIsSelected(tag)"
                :disabled="!tagIsSelected(tag) && selectedTags.length >= NEWS_TAG_LIMIT"
                @change="toggleTag(tag)"
              />
              {{ tag }}
            </label>
          </div>
        </details>
        <BaseInput
          :model-value="form.language"
          placeholder="language (en)"
          @update:model-value="patch({ language: toStringValue($event) })"
        />
      </section>
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #start>
          <BaseButton
            v-if="mode === 'edit'"
            danger
            type="button"
            :disabled="loading"
            @click="emit('delete')"
          >
            delete
          </BaseButton>
        </template>
        <template #primary>
          <ToolbarPillButton family="2xx" :disabled="loading" @click="emit('save')">
            {{ loading ? "saving..." : "save" }}
          </ToolbarPillButton>
        </template>
      </DrawerFooterActions>
    </template>
  </BaseDrawer>
</template>
