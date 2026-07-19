<script setup lang="ts">
import { computed } from "vue";

import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { SELECT_CLASS } from "@/constants/formClasses";
import { NEWS_THEME_LIMIT, NEWS_THEMES } from "@/constants/news";
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

const title = computed(() => (props.mode === "create" ? "new article" : "edit article"));
const selectedThemes = computed(() =>
  props.form.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean),
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

function themeIsSelected(theme: string): boolean {
  return selectedThemes.value.includes(theme);
}

function toggleTheme(theme: string): void {
  const themes = selectedThemes.value;
  if (themes.includes(theme)) {
    patch({ themes: themes.filter((item) => item !== theme).join(", ") });
    return;
  }
  if (themes.length >= NEWS_THEME_LIMIT) return;
  patch({ themes: [...themes, theme].join(", ") });
}
</script>

<template>
  <BaseDrawer :open="open" :title="title" max-width="xl" @close="emit('close')">
    <form class="space-y-6" @submit.prevent="emit('save')">
      <section class="space-y-4">
        <h3 class="text-sm font-medium text-surface-mid">publishing</h3>
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
          placeholder="article url (https://...)"
          aria-label="article url (https://...)"
          type="url"
          @update:model-value="patch({ source_url: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_name"
          placeholder="source name (e.g. DW)"
          aria-label="source name (e.g. DW)"
          @update:model-value="patch({ source_name: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_feed_url"
          placeholder="source feed/home url (https://www.dw.com/)"
          aria-label="source feed/home url (https://www.dw.com/)"
          type="url"
          @update:model-value="patch({ source_feed_url: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.source_published_at"
          type="datetime-local"
          aria-label="source published at"
          @update:model-value="patch({ source_published_at: toStringValue($event) })"
        />
        <select
          :value="form.status"
          aria-label="status"
          :class="SELECT_CLASS"
          @change="patch({ status: ($event.target as HTMLSelectElement).value as NewsStatus })"
        >
          <option value="draft">draft</option>
          <option value="published">published</option>
          <option value="unpublished">unpublished</option>
          <option value="failed">failed</option>
        </select>
      </section>

      <section class="space-y-4">
        <h3 class="text-sm font-medium text-surface-mid">article</h3>
        <BaseInput
          v-if="mode === 'edit'"
          :model-value="form.slug"
          placeholder="slug (article-url-slug)"
          aria-label="slug (article-url-slug)"
          @update:model-value="patch({ slug: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.title"
          placeholder="title"
          aria-label="title"
          @update:model-value="patch({ title: toStringValue($event) })"
        />
        <BaseInput
          :model-value="form.original_title"
          placeholder="original title"
          aria-label="original title"
          @update:model-value="patch({ original_title: toStringValue($event) })"
        />
        <BaseTextarea
          :model-value="form.summary"
          :rows="4"
          placeholder="summary"
          aria-label="summary"
          @update:model-value="patch({ summary: toStringValue($event) })"
        />
        <fieldset class="space-y-2">
          <legend class="text-sm text-surface-mid">
            themes
            <span class="text-xs text-surface-muted">
              ({{ selectedThemes.length }}/{{ NEWS_THEME_LIMIT }})
            </span>
          </legend>
          <div class="flex flex-wrap gap-2">
            <label
              v-for="theme in NEWS_THEMES"
              :key="theme"
              class="inline-flex cursor-pointer items-center gap-2 rounded border border-surface-border px-3 py-1.5 text-xs transition-colors"
              :class="{
                'border-accent-blue text-surface-light': themeIsSelected(theme),
                'text-surface-mid': !themeIsSelected(theme),
                'opacity-50': !themeIsSelected(theme) && selectedThemes.length >= NEWS_THEME_LIMIT,
              }"
            >
              <input
                type="checkbox"
                :checked="themeIsSelected(theme)"
                :disabled="!themeIsSelected(theme) && selectedThemes.length >= NEWS_THEME_LIMIT"
                @change="toggleTheme(theme)"
              />
              {{ theme }}
            </label>
          </div>
        </fieldset>
        <BaseInput
          :model-value="form.language"
          placeholder="language (en)"
          aria-label="language (en)"
          @update:model-value="patch({ language: toStringValue($event) })"
        />
      </section>
    </form>

    <template #footer>
      <div class="flex flex-wrap items-center justify-between gap-3">
        <BaseButton
          v-if="mode === 'edit'"
          variant="ghost"
          danger
          type="button"
          :disabled="loading"
          @click="emit('delete')"
        >
          delete
        </BaseButton>
        <div class="flex gap-3">
          <BaseButton variant="primary" :disabled="loading" @click="emit('save')">
            {{ loading ? "saving..." : "save" }}
          </BaseButton>
          <BaseButton variant="ghost" type="button" @click="emit('close')">cancel</BaseButton>
        </div>
      </div>
    </template>
  </BaseDrawer>
</template>
