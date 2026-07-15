<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsArticleDrawer from "@/components/news/NewsArticleDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BasePagination from "@/components/ui/BasePagination.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import { Card } from "@/components/ui/card";
import {
  NEWS_SUMMARY_MAX_LENGTH,
  NEWS_THEME_LIMIT,
  NEWS_THEME_SET,
  NEWS_TITLE_MAX_LENGTH,
} from "@/constants/news";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type {
  NewsArticle,
  NewsArticleCreate,
  NewsArticleFormData,
  NewsArticleUpdate,
  NewsStatus,
} from "@/types";
import { normalizeHttpUrl, titleFromNewsLink } from "@/utils/newsForms";
import { safeNavigationHref } from "@/utils/safeUrl";

type DrawerMode = "create" | "edit";

const { can } = usePermissions();
const { toast } = useNotify();
const canWrite = computed(() => can("news", "write"));
const drawerOpen = ref(false);
const drawerMode = ref<DrawerMode>("create");
const editingArticleId = ref<number | null>(null);
const form = ref<NewsArticleFormData>(emptyForm());
const lastAutoTitle = ref<string | null>(null);
const metadataRequestId = ref(0);

const {
  articles,
  sources,
  page,
  total,
  totalPages,
  listLoading,
  listError,
  actionLoading,
  hasNextPage,
  countLabel,
  loadNews,
  loadSources,
  goToPage,
  ingestNews,
  loadArticleMetadata,
  createArticle,
  updateArticle,
  deleteArticle,
  repostToTelegram,
} = useNews();

useScrollListFingerprint(
  () => `${page.value}:${total.value}:${articles.value[0]?.id ?? ""}`,
);

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
    themes: "world",
    language: "en",
    published_at: "",
    telegram_message_id: "",
    ai_model: "",
    ai_input_hash: "",
    ingest_error: "",
  };
}

function formFromArticle(article: NewsArticle): NewsArticleFormData {
  return {
    slug: article.slug,
    status: article.status,
    source_id: article.source_id,
    source_name: article.source_name,
    source_url: article.source_url,
    source_feed_url: article.source_feed_url,
    source_published_at: article.source_published_at?.slice(0, 16) ?? "",
    original_title: article.original_title,
    title: article.title,
    summary: article.summary,
    bullets: [],
    themes: article.themes.join(", "),
    language: article.language,
    published_at: article.published_at?.slice(0, 16) ?? "",
    telegram_message_id: article.telegram_message_id?.toString() ?? "",
    ai_model: article.ai_model ?? "",
    ai_input_hash: article.ai_input_hash ?? "",
    ingest_error: article.ingest_error ?? "",
  };
}

function parsedThemes(): string[] {
  return form.value.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean);
}

function canReplaceAutoValue(currentValue: string, lastAutoValue: string | null): boolean {
  return !currentValue.trim() || (lastAutoValue !== null && currentValue === lastAutoValue);
}

function normalizedDateTime(value: string): string | null {
  if (!value.trim()) return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed.toISOString();
}

function normalizedSourcePublishedAt(): string | null {
  return normalizedDateTime(form.value.source_published_at);
}

function optionalText(value: string): string | null {
  const trimmed = value.trim();
  return trimmed || null;
}

function sourcePublishedAtPayload(): string | null {
  return normalizedSourcePublishedAt();
}

function sourceUrlPayload(): string | null {
  return normalizeHttpUrl(form.value.source_url);
}

function sourceFeedUrlPayload(): string | undefined {
  const sourceFeedUrl = normalizeHttpUrl(form.value.source_feed_url);
  return sourceFeedUrl ?? undefined;
}

function slugPayload(): string | undefined {
  const slug = form.value.slug.trim();
  return slug || undefined;
}

function applySource(sourceId: number | null): void {
  const source = sources.value.find((item) => item.id === sourceId);
  form.value = {
    ...form.value,
    source_id: sourceId,
    source_name: source?.name ?? form.value.source_name,
    source_feed_url: source?.feed_url ?? form.value.source_feed_url,
  };
}

async function hydrateFromSourceUrl(sourceUrl: string): Promise<void> {
  const requestId = metadataRequestId.value + 1;
  metadataRequestId.value = requestId;
  const metadata = await loadArticleMetadata(sourceUrl);
  if (!metadata || requestId !== metadataRequestId.value) return;
  await loadSources();
  const nextValues: Partial<NewsArticleFormData> = {
    source_url: metadata.source_url,
    source_id: metadata.source_id,
    source_name: metadata.source_name,
    source_feed_url: metadata.source_feed_url,
  };
  if (metadata.title && canReplaceAutoValue(form.value.title, lastAutoTitle.value)) {
    nextValues.title = metadata.title;
    lastAutoTitle.value = metadata.title;
  }
  form.value = { ...form.value, ...nextValues };
}

function dateIsInvalid(value: string, normalizedValue: string | null): boolean {
  return Boolean(value.trim()) && normalizedValue === null;
}

function withSourceUrlDefaults(nextForm: NewsArticleFormData): NewsArticleFormData {
  const sourceUrl = normalizeHttpUrl(nextForm.source_url);
  if (!sourceUrl) return { ...nextForm, source_feed_url: "" };

  const nextValues: Partial<NewsArticleFormData> = {
    source_feed_url: sourceUrl,
  };
  const autoTitle = titleFromNewsLink(sourceUrl);
  if (autoTitle && canReplaceAutoValue(nextForm.title, lastAutoTitle.value)) {
    nextValues.title = autoTitle;
    lastAutoTitle.value = autoTitle;
  }
  return { ...nextForm, ...nextValues };
}

async function updateForm(nextForm: NewsArticleFormData): Promise<void> {
  if (nextForm.source_id !== form.value.source_id) {
    applySource(nextForm.source_id);
    return;
  }
  if (nextForm.source_url !== form.value.source_url) {
    const nextWithDefaults = withSourceUrlDefaults(nextForm);
    form.value = nextWithDefaults;
    const sourceUrl = normalizeHttpUrl(nextWithDefaults.source_url);
    if (sourceUrl) await hydrateFromSourceUrl(sourceUrl);
    return;
  }
  form.value = nextForm;
}

function validateForm(): boolean {
  const title = form.value.title.trim();
  const summary = form.value.summary.trim();
  const themes = parsedThemes();

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
  const sourceUrl = sourceUrlPayload();
  if (!sourceUrl) {
    toast("Source URL must start with http:// or https://", "error");
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
  if (dateIsInvalid(form.value.source_published_at, normalizedSourcePublishedAt())) {
    toast("Source published date is invalid", "error");
    return false;
  }
  return true;
}

function buildCreatePayload(): NewsArticleCreate {
  const sourceUrl = sourceUrlPayload() ?? form.value.source_url.trim();
  const title = form.value.title.trim();
  const originalTitle = form.value.original_title.trim() || title;
  return {
    status: form.value.status,
    source_id: form.value.source_id,
    source_name: optionalText(form.value.source_name) ?? undefined,
    source_url: sourceUrl,
    source_feed_url: sourceFeedUrlPayload(),
    source_published_at: sourcePublishedAtPayload(),
    original_title: originalTitle,
    title,
    summary: form.value.summary.trim(),
    themes: parsedThemes(),
    language: form.value.language.trim() || "en",
  };
}

function buildUpdatePayload(): NewsArticleUpdate {
  return {
    ...buildCreatePayload(),
    slug: slugPayload(),
  };
}

async function loadAdminNews(): Promise<void> {
  await loadNews({ admin: true });
}

async function runIngest(): Promise<void> {
  await ingestNews();
  await loadAdminNews();
}

async function setStatus(articleId: number, status: NewsStatus): Promise<void> {
  await updateArticle(articleId, { status });
  await loadAdminNews();
}

async function repost(articleId: number): Promise<void> {
  await repostToTelegram(articleId);
  await loadAdminNews();
}

function openCreate(): void {
  drawerMode.value = "create";
  editingArticleId.value = null;
  lastAutoTitle.value = null;
  form.value = emptyForm();
  drawerOpen.value = true;
}

function openEdit(article: NewsArticle): void {
  drawerMode.value = "edit";
  editingArticleId.value = article.id;
  lastAutoTitle.value = null;
  form.value = formFromArticle(article);
  drawerOpen.value = true;
}

function openEditableArticle(article: NewsArticle): void {
  if (!canWrite.value) return;
  openEdit(article);
}

function onArticleKeydown(event: KeyboardEvent, article: NewsArticle): void {
  if (!canWrite.value || (event.key !== "Enter" && event.key !== " ")) return;
  event.preventDefault();
  openEdit(article);
}

function closeDrawer(): void {
  drawerOpen.value = false;
  editingArticleId.value = null;
}

async function saveDrawer(): Promise<void> {
  if (!validateForm()) return;
  if (drawerMode.value === "create") {
    const created = await createArticle(buildCreatePayload());
    if (!created) return;
  } else if (editingArticleId.value) {
    const updated = await updateArticle(editingArticleId.value, buildUpdatePayload());
    if (!updated) return;
  }
  closeDrawer();
  await loadAdminNews();
}

async function deleteDrawerArticle(): Promise<void> {
  if (!editingArticleId.value) return;
  const title = form.value.title.trim() || "this article";
  if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) return;
  if (!(await deleteArticle(editingArticleId.value))) return;
  closeDrawer();
  await loadAdminNews();
}

onMounted(async () => {
  await Promise.all([loadAdminNews(), loadSources()]);
});

watch(page, () => {
  void loadAdminNews();
});
</script>

<template>
  <AdminPageLayout title="news" max-width="xl">
    <header class="page-intro">
      <p class="text-sm text-surface-mid mb-2">
        Manage curated news articles, ingestion, and Telegram delivery.
      </p>
      <p class="text-xs text-surface-muted mb-4">{{ countLabel }}</p>
      <div v-if="canWrite" class="flex flex-wrap gap-2">
        <BaseButton variant="ghost" size="sm" :disabled="actionLoading" @click="runIngest">
          Run ingest
        </BaseButton>
        <BaseButton variant="primary" size="sm" :disabled="actionLoading" @click="openCreate">
          New article
        </BaseButton>
      </div>
    </header>

    <section v-if="listLoading" class="space-y-3" aria-busy="true" aria-label="Loading news">
      <Card v-for="i in 5" :key="i" class="h-36 animate-pulse" />
    </section>

    <ErrorState
      v-else-if="listError"
      :message="listError"
      show-retry
      @retry="loadAdminNews"
    />

    <section v-else-if="articles.length" class="space-y-3 min-w-0">
      <Card
        v-for="item in articles"
        :key="item.id"
        as="article"
        variant="compact"
        class="min-w-0"
        :hoverable="canWrite"
        :interactive="canWrite"
        :role="canWrite ? 'button' : undefined"
        :tabindex="canWrite ? 0 : undefined"
        :class="canWrite ? 'cursor-pointer' : undefined"
        @click="openEditableArticle(item)"
        @keydown="onArticleKeydown($event, item)"
      >
        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.status }}</span>
          <span aria-hidden="true">/</span>
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="item.published_at ?? item.created_at">
            {{ formatNewsDate(item.published_at ?? item.created_at) }}
          </time>
          <span v-if="item.telegram_message_id" class="text-accent-blue">
            Telegram #{{ item.telegram_message_id }}
          </span>
        </div>

        <h2 class="card-title mb-2 break-words">
          {{ item.title }}
        </h2>
        <p class="text-sm text-surface-mid mb-3 break-words">{{ item.summary }}</p>

        <div class="mb-4 flex flex-wrap gap-2">
          <span
            v-for="theme in item.themes"
            :key="theme"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
          >
            {{ theme }}
          </span>
        </div>

        <div class="flex flex-wrap gap-2" @click.stop @keydown.stop>
          <BaseButton
            v-if="canWrite && item.status !== 'published'"
            variant="ghost"
            size="sm"
            :disabled="actionLoading"
            @click="setStatus(item.id, 'published')"
          >
            Publish
          </BaseButton>
          <BaseButton
            v-if="canWrite && item.status === 'published'"
            variant="ghost"
            size="sm"
            :disabled="actionLoading"
            @click="setStatus(item.id, 'unpublished')"
          >
            Unpublish
          </BaseButton>
          <BaseButton
            v-if="canWrite"
            variant="ghost"
            size="sm"
            :disabled="actionLoading"
            @click="repost(item.id)"
          >
            Repost Telegram
          </BaseButton>
          <a
            v-if="safeNavigationHref(item.source_url)"
            :href="safeNavigationHref(item.source_url) ?? '#'"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center px-3 py-1.5 text-xs text-accent-blue hover:underline"
            @click.stop
          >
            Source
          </a>
        </div>
      </Card>
    </section>

    <EmptyState
      v-else
      title="No articles"
      description="No news articles match this filter. Run ingestion after configuring trusted sources."
    />

    <BasePagination
      v-if="!listLoading && !listError && (articles.length > 0 || page > 1)"
      class="mt-8"
      aria-label="Admin news pagination"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      @prev="goToPage(page - 1)"
      @next="goToPage(page + 1)"
    />

    <NewsArticleDrawer
      v-if="canWrite"
      :open="drawerOpen"
      :mode="drawerMode"
      :form="form"
      :sources="sources"
      :loading="actionLoading"
      @update:form="updateForm"
      @close="closeDrawer"
      @delete="deleteDrawerArticle"
      @save="saveDrawer"
    />
  </AdminPageLayout>
</template>
