<script setup lang="ts">
import { ref } from "vue";

import AdminFilterChip from "@/components/admin/AdminFilterChip.vue";
import ChevronIcon from "@/components/icons/ChevronIcon.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { newsStatusClass } from "@/constants/filterColors";
import { NEWS_STATUSES, NEWS_THEME_LIMIT, NEWS_THEMES } from "@/constants/news";
import type { NewsArticleFormData, NewsStatus } from "@/types";

const form = defineModel<NewsArticleFormData>({ required: true });

const props = defineProps<{
  canWrite: boolean;
}>();

const themesOpen = ref(false);

function parsedThemes(): string[] {
  return form.value.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean);
}

function themeIsSelected(theme: string): boolean {
  return parsedThemes().includes(theme);
}

function selectedThemesLabel(): string {
  const themes = parsedThemes();
  return themes.length > 0 ? themes.join(", ") : "none";
}

function setStatus(status: NewsStatus): void {
  if (!props.canWrite) return;
  form.value.status = status;
}

function toggleTheme(theme: string): void {
  if (!props.canWrite) return;
  const themes = parsedThemes();
  if (themes.includes(theme)) {
    form.value.themes = themes.filter((item) => item !== theme).join(", ");
    return;
  }
  if (themes.length >= NEWS_THEME_LIMIT) return;
  form.value.themes = [...themes, theme].join(", ");
}

function onThemesToggle(event: Event): void {
  themesOpen.value = (event.target as HTMLDetailsElement).open;
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
        class="grid grid-cols-2 gap-2 sm:col-span-2 sm:grid-cols-4"
        role="group"
        aria-label="status"
      >
        <AdminFilterChip
          v-for="status in NEWS_STATUSES"
          :key="status"
          :label="status"
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
      @toggle="onThemesToggle"
    >
      <summary
        class="flex cursor-pointer list-none items-center gap-1.5 text-sm text-surface-mid [&::-webkit-details-marker]:hidden"
      >
        <ChevronIcon :open="themesOpen" />
        themes ({{ parsedThemes().length }}/{{ NEWS_THEME_LIMIT }})
        <span class="text-xs text-surface-muted"> — {{ selectedThemesLabel() }}</span>
      </summary>
      <div class="mt-3 flex flex-wrap gap-2">
        <label
          v-for="theme in NEWS_THEMES"
          :key="theme"
          :for="`news-edit-theme-${theme}`"
          class="inline-flex cursor-pointer items-center gap-2 rounded border border-surface-border px-3 py-1.5 text-xs transition-colors"
          :class="{
            'border-accent-blue text-surface-light': themeIsSelected(theme),
            'text-surface-mid': !themeIsSelected(theme),
            'opacity-50': !themeIsSelected(theme) && parsedThemes().length >= NEWS_THEME_LIMIT,
          }"
        >
          <input
            :id="`news-edit-theme-${theme}`"
            type="checkbox"
            :checked="themeIsSelected(theme)"
            :disabled="
              !canWrite || (!themeIsSelected(theme) && parsedThemes().length >= NEWS_THEME_LIMIT)
            "
            @change="toggleTheme(theme)"
          />
          {{ theme }}
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
