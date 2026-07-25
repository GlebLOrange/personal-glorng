<script setup lang="ts">
import { computed } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseDrawer from "@/components/ui/BaseDrawer.vue";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import DrawerFooterActions from "@/components/ui/DrawerFooterActions.vue";
import ToolbarPillButton from "@/components/ui/ToolbarPillButton.vue";
import { newsStatusClass } from "@/constants/filterColors";
import { SELECT_CLASS } from "@/constants/formClasses";
import { NEWS_STATUSES, NEWS_THEME_LIMIT, NEWS_THEMES } from "@/constants/news";
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
const selectedThemesLabel = computed(() =>
  selectedThemes.value.length > 0 ? selectedThemes.value.join(", ") : "none",
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
  <BaseDrawer :open="open" :title="title" max-width="2xl" @close="emit('close')">
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
        <div class="grid grid-cols-2 gap-2 sm:grid-cols-4" role="group" aria-label="status">
          <AdminFilterChip
            v-for="status in NEWS_STATUSES"
            :key="status"
            :label="status"
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
        <details class="rounded border border-surface-border px-3 py-2">
          <summary class="cursor-pointer text-sm text-surface-mid">
            themes ({{ selectedThemes.length }}/{{ NEWS_THEME_LIMIT }})
            <span class="text-xs text-surface-muted"> — {{ selectedThemesLabel }}</span>
          </summary>
          <div class="mt-3 flex flex-wrap gap-2">
            <label
              v-for="theme in NEWS_THEMES"
              :key="theme"
              :for="`news-drawer-theme-${theme}`"
              class="inline-flex cursor-pointer items-center gap-2 rounded border border-surface-border px-3 py-1.5 text-xs transition-colors"
              :class="{
                'border-accent-blue text-surface-light': themeIsSelected(theme),
                'text-surface-mid': !themeIsSelected(theme),
                'opacity-50': !themeIsSelected(theme) && selectedThemes.length >= NEWS_THEME_LIMIT,
              }"
            >
              <input
                :id="`news-drawer-theme-${theme}`"
                type="checkbox"
                :checked="themeIsSelected(theme)"
                :disabled="!themeIsSelected(theme) && selectedThemes.length >= NEWS_THEME_LIMIT"
                @change="toggleTheme(theme)"
              />
              {{ theme }}
            </label>
          </div>
        </details>
        <BaseInput
          :model-value="form.language"
          placeholder="language (en)"
          aria-label="language (en)"
          @update:model-value="patch({ language: toStringValue($event) })"
        />
      </section>
    </form>

    <template #footer>
      <DrawerFooterActions>
        <template #start>
          <BaseButton
            v-if="mode === 'edit'"
            variant="ghost"
            danger
            type="button"
            class="hover:enabled:border-transparent focus-visible:border-transparent"
            :disabled="loading"
            @click="emit('delete')"
          >
            delete
          </BaseButton>
        </template>
        <template #dismiss>
          <BaseButton
            variant="ghost"
            danger
            type="button"
            class="hover:enabled:border-transparent focus-visible:border-transparent"
            @click="emit('close')"
          >
            cancel
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
