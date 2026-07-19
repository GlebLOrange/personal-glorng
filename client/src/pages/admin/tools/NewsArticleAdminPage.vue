<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import BaseInput from "@/components/ui/BaseInput.vue";
import BaseTextarea from "@/components/ui/BaseTextarea.vue";
import { SELECT_CLASS } from "@/constants/formClasses";
import {
  NEWS_SUMMARY_MAX_LENGTH,
  NEWS_THEME_LIMIT,
  NEWS_THEME_SET,
  NEWS_THEMES,
  NEWS_TITLE_MAX_LENGTH,
} from "@/constants/news";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type { NewsArticle, NewsArticleFormData, NewsArticleUpdate } from "@/types";
import { normalizeHttpUrl } from "@/utils/newsForms";

const route = useRoute();
const { toast } = useNotify();
const { can } = usePermissions();
const canWrite = computed(() => can("news", "write"));
const articleId = computed(() => Number(route.params.id));

const {
  article,
  sources,
  detailLoading,
  detailError,
  actionLoading,
  loadAdminArticle,
  loadSources,
  updateArticle,
} = useNews();

useScrollListFingerprint(
  () => `${articleId.value}:${article.value?.id ?? ""}:${article.value?.updated_at ?? ""}`,
);

const form = ref<NewsArticleFormData>(emptyForm());

function emptyForm(): NewsArticleFormData {
  return {
    slug: "",
    status: "draft",
    source_id: null,
    source_name: "",
    source_url: "",
    source_feed_url: "",
    source_published_at: "",
    original_title: "",
    title: "",
    summary: "",
    bullets: [],
    themes: "",
    language: "en",
    published_at: "",
    telegram_message_id: "",
    ai_model: "",
    ai_input_hash: "",
    ingest_error: "",
  };
}

function formFromArticle(item: NewsArticle): NewsArticleFormData {
  return {
    slug: item.slug,
    status: item.status,
    source_id: item.source_id,
    source_name: item.source_name,
    source_url: item.source_url,
    source_feed_url: item.source_feed_url,
    source_published_at: item.source_published_at?.slice(0, 16) ?? "",
    original_title: item.original_title,
    title: item.title,
    summary: item.summary,
    bullets: [],
    themes: item.themes.join(", "),
    language: item.language,
    published_at: item.published_at?.slice(0, 16) ?? "",
    telegram_message_id: item.telegram_message_id?.toString() ?? "",
    ai_model: item.ai_model ?? "",
    ai_input_hash: item.ai_input_hash ?? "",
    ingest_error: item.ingest_error ?? "",
  };
}

function parsedThemes(): string[] {
  return form.value.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean);
}

function normalizedDateTime(value: string): string | null {
  if (!value.trim()) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed || null;
}

function sourceFeedUrlPayload(): string | undefined {
  return normalizeHttpUrl(form.value.source_feed_url) ?? undefined;
}

function dateIsInvalid(value: string, normalizedValue: string | null): boolean {
  return Boolean(value.trim()) && normalizedValue === null;
}

function validateForm(): boolean {
  const title = form.value.title.trim();
  const summary = form.value.summary.trim();
  const themes = parsedThemes();

  if (!canWrite.value) return false;
  if (!form.value.slug.trim()) {
    toast("Slug is required", "error");
    return false;
  }
  if (!title) {
    toast("Title is required", "error");
    return false;
  }
  if (title.length > NEWS_TITLE_MAX_LENGTH) {
    toast(`Title must be ${NEWS_TITLE_MAX_LENGTH} characters or fewer`, "error");
    return false;
  }
  if (!summary) {
    toast("Summary is required", "error");
    return false;
  }
  if (summary.length > NEWS_SUMMARY_MAX_LENGTH) {
    toast(`Summary must be ${NEWS_SUMMARY_MAX_LENGTH} characters or fewer`, "error");
    return false;
  }
  if (!normalizeHttpUrl(form.value.source_url)) {
    toast("Source URL must start with http:// or https://", "error");
    return false;
  }
  if (form.value.source_feed_url.trim() && !sourceFeedUrlPayload()) {
    toast("Source feed/home URL must start with http:// or https://", "error");
    return false;
  }
  if (themes.length < 1) {
    toast("Add at least one theme", "error");
    return false;
  }
  if (themes.length > NEWS_THEME_LIMIT) {
    toast(`Choose no more than ${NEWS_THEME_LIMIT} themes`, "error");
    return false;
  }
  if (themes.some((theme) => !NEWS_THEME_SET.has(theme))) {
    toast("Choose only supported news themes", "error");
    return false;
  }
  if (
    dateIsInvalid(
      form.value.source_published_at,
      normalizedDateTime(form.value.source_published_at),
    )
  ) {
    toast("Source published date is invalid", "error");
    return false;
  }
  return true;
}

function buildUpdatePayload(): NewsArticleUpdate {
  return {
    slug: form.value.slug.trim(),
    status: form.value.status,
    source_id: form.value.source_id,
    source_name: optionalText(form.value.source_name) ?? undefined,
    source_url: normalizeHttpUrl(form.value.source_url) ?? form.value.source_url.trim(),
    source_feed_url: sourceFeedUrlPayload(),
    source_published_at: normalizedDateTime(form.value.source_published_at),
    original_title: form.value.original_title.trim() || form.value.title.trim(),
    title: form.value.title.trim(),
    summary: form.value.summary.trim(),
    themes: parsedThemes(),
    language: form.value.language.trim() || "en",
  };
}

function themeIsSelected(theme: string): boolean {
  return parsedThemes().includes(theme);
}

function toggleTheme(theme: string): void {
  const themes = parsedThemes();
  if (themes.includes(theme)) {
    form.value.themes = themes.filter((item) => item !== theme).join(", ");
    return;
  }
  if (themes.length >= NEWS_THEME_LIMIT) return;
  form.value.themes = [...themes, theme].join(", ");
}

function applySource(sourceId: number | null): void {
  const source = sources.value.find((item) => item.id === sourceId);
  form.value.source_id = sourceId;
  if (!source) return;
  form.value.source_name = source.name;
  form.value.source_feed_url = source.feed_url;
}

async function loadCurrentArticle(): Promise<void> {
  if (!Number.isInteger(articleId.value) || articleId.value <= 0) return;
  await loadAdminArticle(articleId.value);
  if (article.value) form.value = formFromArticle(article.value);
}

async function saveArticle(): Promise<void> {
  if (!article.value || !validateForm()) return;
  const updated = await updateArticle(article.value.id, buildUpdatePayload());
  if (!updated) return;
  article.value = updated;
  form.value = formFromArticle(updated);
}

onMounted(async () => {
  await Promise.all([loadCurrentArticle(), loadSources()]);
});

watch(articleId, () => {
  void loadCurrentArticle();
});
</script>

<template>
  <AdminPageLayout hub="tools" title="edit news article" max-width="xl" back-to="/admin/tools/news">
    <header v-if="canWrite && article" class="page-intro">
      <div class="flex flex-wrap gap-2">
        <BaseButton variant="primary" :disabled="actionLoading" @click="saveArticle">
          {{ actionLoading ? "saving..." : "save article" }}
        </BaseButton>
      </div>
    </header>

    <div class="min-w-0">

    <Card v-if="!Number.isInteger(articleId) || articleId <= 0" role="alert">
      <p class="text-sm text-accent-golden">Invalid news article id.</p>
    </Card>

    <Card
      v-else-if="detailLoading"
      class="h-96 animate-pulse"
      aria-busy="true"
      aria-label="Loading news article"
    />

    <Card v-else-if="detailError" role="alert">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <p class="text-sm text-accent-golden">{{ detailError }}</p>
        <BaseButton variant="ghost" size="sm" @click="loadCurrentArticle">retry</BaseButton>
      </div>
    </Card>

    <form
      v-else-if="article"
      class="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1fr)_22rem]"
      @submit.prevent="saveArticle"
    >
      <div class="space-y-6">
        <Card>
          <h2 class="card-title mb-4">article</h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <BaseInput
              v-model="form.slug"
              placeholder="slug"
              aria-label="slug"
              :disabled="!canWrite"
            />
            <select
              v-model="form.status"
              :class="SELECT_CLASS"
              aria-label="status"
              :disabled="!canWrite"
            >
              <option value="draft">draft</option>
              <option value="published">published</option>
              <option value="unpublished">unpublished</option>
              <option value="failed">failed</option>
            </select>
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
              aria-label="language (en)"
              :disabled="!canWrite"
            />
          </div>
          <fieldset class="mt-4 space-y-2">
            <legend class="text-sm text-surface-mid">
              themes
              <span class="text-xs text-surface-muted">
                ({{ parsedThemes().length }}/{{ NEWS_THEME_LIMIT }})
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
                  'opacity-50':
                    !themeIsSelected(theme) && parsedThemes().length >= NEWS_THEME_LIMIT,
                }"
              >
                <input
                  type="checkbox"
                  :checked="themeIsSelected(theme)"
                  :disabled="
                    !canWrite ||
                    (!themeIsSelected(theme) && parsedThemes().length >= NEWS_THEME_LIMIT)
                  "
                  @change="toggleTheme(theme)"
                />
                {{ theme }}
              </label>
            </div>
          </fieldset>
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

        <Card>
          <h2 class="card-title mb-4">source</h2>
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
            <select
              :value="form.source_id ?? ''"
              :class="SELECT_CLASS"
              aria-label="source"
              :disabled="!canWrite"
              @change="applySource(Number(($event.target as HTMLSelectElement).value) || null)"
            >
              <option value="">auto from URL host</option>
              <option v-for="source in sources" :key="source.id" :value="source.id">
                {{ source.name }}{{ source.host ? ` (${source.host})` : "" }}
              </option>
            </select>
            <BaseInput
              v-model="form.source_name"
              placeholder="source name"
              aria-label="source name"
              :disabled="!canWrite"
            />
            <BaseInput
              v-model="form.source_url"
              placeholder="article url"
              aria-label="article url"
              type="url"
              :disabled="!canWrite"
            />
            <BaseInput
              v-model="form.source_feed_url"
              placeholder="source feed/home url"
              aria-label="source feed/home url"
              type="url"
              :disabled="!canWrite"
            />
            <BaseInput
              v-model="form.source_published_at"
              type="datetime-local"
              aria-label="source published at"
              :disabled="!canWrite"
            />
          </div>
        </Card>
      </div>

      <aside class="space-y-6">
        <Card>
          <h2 class="card-title mb-4">system fields</h2>
          <dl class="space-y-3 text-sm">
            <div>
              <dt class="text-surface-muted">ID</dt>
              <dd class="font-data text-surface-light">{{ article.id }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Created</dt>
              <dd class="text-surface-light">{{ formatNewsDate(article.created_at) }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Updated</dt>
              <dd class="text-surface-light">{{ formatNewsDate(article.updated_at) }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Source ID</dt>
              <dd class="font-data text-surface-light">{{ article.source_id ?? "none" }}</dd>
            </div>
            <div>
              <dt class="text-surface-muted">Telegram message</dt>
              <dd class="font-data text-surface-light">
                {{ article.telegram_message_id ?? "none" }}
              </dd>
            </div>
          </dl>
        </Card>

        <Card>
          <h2 class="card-title mb-4">current preview</h2>
          <p class="mb-2 text-xs text-surface-muted">
            {{ form.status }} / {{ form.source_name || "unknown source" }}
          </p>
          <h3 class="mb-3 text-lg font-semibold text-surface-light">
            {{ form.title || "Untitled" }}
          </h3>
          <p class="text-sm text-surface-mid">{{ form.summary || "No summary yet." }}</p>
          <div class="mt-4 flex flex-wrap gap-2">
            <span
              v-for="theme in parsedThemes()"
              :key="theme"
              class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
            >
              {{ theme }}
            </span>
          </div>
        </Card>

        <Card v-if="!canWrite">
          <p class="text-sm text-surface-mid">
            You have `news:read`, so this page is read-only. Saving requires `news:write`.
          </p>
        </Card>
      </aside>
    </form>
    </div>
  </AdminPageLayout>
</template>
