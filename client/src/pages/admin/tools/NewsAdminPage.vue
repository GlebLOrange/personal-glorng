<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import NewsArticleDrawer from "@/components/news/NewsArticleDrawer.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { useNotify } from "@/composables/useNotify";
import { usePermissions } from "@/composables/usePermissions";
import type {
  NewsArticle,
  NewsArticleCreate,
  NewsArticleFormData,
  NewsArticleUpdate,
  NewsStatus,
} from "@/types";

type StatusFilter = NewsStatus | "all";
type DrawerMode = "create" | "edit";

const statusFilter = ref<StatusFilter>("all");
const { can } = usePermissions();
const { toast } = useNotify();
const canWrite = computed(() => can("news", "write"));
const drawerOpen = ref(false);
const drawerMode = ref<DrawerMode>("create");
const editingArticleId = ref<number | null>(null);
const form = ref<NewsArticleFormData>(emptyForm());

const {
  articles,
  themes,
  activeTheme,
  page,
  listLoading,
  listError,
  actionLoading,
  hasNextPage,
  countLabel,
  loadNews,
  loadThemes,
  setTheme,
  goToPage,
  ingestNews,
  createArticle,
  updateArticle,
  deleteArticle,
  repostToTelegram,
} = useNews();

function emptyForm(): NewsArticleFormData {
  return {
    status: "published",
    source_name: "",
    source_url: "",
    source_feed_url: "",
    source_published_at: "",
    original_title: "",
    title: "",
    summary: "",
    bullets: ["", ""],
    themes: "world",
    language: "en",
  };
}

function formFromArticle(article: NewsArticle): NewsArticleFormData {
  const bullets = article.bullets.length ? [...article.bullets] : ["", ""];
  while (bullets.length < 2) bullets.push("");
  return {
    status: article.status,
    source_name: article.source_name,
    source_url: article.source_url,
    source_feed_url: article.source_feed_url,
    source_published_at: article.source_published_at?.slice(0, 16) ?? "",
    original_title: article.original_title,
    title: article.title,
    summary: article.summary,
    bullets,
    themes: article.themes.join(", "),
    language: article.language,
  };
}

function parsedThemes(): string[] {
  return form.value.themes
    .split(",")
    .map((theme) => theme.trim())
    .filter(Boolean);
}

function parsedBullets(): string[] {
  return form.value.bullets.map((bullet) => bullet.trim()).filter(Boolean);
}

function isHttpUrl(value: string): boolean {
  return value.startsWith("http://") || value.startsWith("https://");
}

function normalizedPublishedAt(): string | null {
  if (!form.value.source_published_at.trim()) return null;
  const value = new Date(form.value.source_published_at);
  return Number.isNaN(value.getTime()) ? null : value.toISOString();
}

function validateForm(): boolean {
  if (!form.value.title.trim()) {
    toast("Title is required", "error");
    return false;
  }
  if (!form.value.summary.trim()) {
    toast("Summary is required", "error");
    return false;
  }
  if (!form.value.source_name.trim() || !form.value.original_title.trim()) {
    toast("Source name and original title are required", "error");
    return false;
  }
  if (!isHttpUrl(form.value.source_url) || !isHttpUrl(form.value.source_feed_url)) {
    toast("Source and feed URLs must start with http:// or https://", "error");
    return false;
  }
  if (parsedBullets().length < 2) {
    toast("Add at least two key points", "error");
    return false;
  }
  if (parsedThemes().length < 1) {
    toast("Add at least one theme", "error");
    return false;
  }
  if (form.value.source_published_at.trim() && normalizedPublishedAt() === null) {
    toast("Source published date is invalid", "error");
    return false;
  }
  return true;
}

function buildCreatePayload(): NewsArticleCreate {
  return {
    status: form.value.status,
    source_name: form.value.source_name.trim(),
    source_url: form.value.source_url.trim(),
    source_feed_url: form.value.source_feed_url.trim(),
    source_published_at: normalizedPublishedAt(),
    original_title: form.value.original_title.trim(),
    title: form.value.title.trim(),
    summary: form.value.summary.trim(),
    bullets: parsedBullets(),
    themes: parsedThemes(),
    language: form.value.language.trim() || "en",
  };
}

function buildUpdatePayload(): NewsArticleUpdate {
  return buildCreatePayload();
}

function statusParam(): NewsStatus | null {
  return statusFilter.value === "all" ? null : statusFilter.value;
}

async function loadAdminNews(): Promise<void> {
  await loadNews({ admin: true, status: statusParam() });
}

async function runIngest(): Promise<void> {
  await ingestNews();
  await loadAdminNews();
}

async function setStatus(articleId: number, status: NewsStatus): Promise<void> {
  await updateArticle(articleId, { status });
  await loadAdminNews();
}

async function removeArticle(articleId: number, title: string): Promise<void> {
  if (!window.confirm(`Delete "${title}"? This cannot be undone.`)) return;
  if (await deleteArticle(articleId)) {
    await loadAdminNews();
  }
}

async function repost(articleId: number): Promise<void> {
  await repostToTelegram(articleId);
  await loadAdminNews();
}

function openCreate(): void {
  drawerMode.value = "create";
  editingArticleId.value = null;
  form.value = emptyForm();
  drawerOpen.value = true;
}

function openEdit(article: NewsArticle): void {
  drawerMode.value = "edit";
  editingArticleId.value = article.id;
  form.value = formFromArticle(article);
  drawerOpen.value = true;
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
  await loadThemes();
}

onMounted(async () => {
  await Promise.all([loadAdminNews(), loadThemes()]);
});

watch([activeTheme, page, statusFilter], () => {
  void loadAdminNews();
});
</script>

<template>
  <AdminPageLayout title="news" max-width="xl">
    <div class="mb-6 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
      <div>
        <p class="text-sm text-surface-mid mb-2">
          Manage curated news articles, ingestion, and Telegram delivery.
        </p>
        <p class="text-xs text-surface-muted">{{ countLabel }}</p>
      </div>
      <div v-if="canWrite" class="flex flex-wrap gap-2">
        <BaseButton variant="ghost" size="sm" :disabled="actionLoading" @click="runIngest">
          Run ingest
        </BaseButton>
        <BaseButton variant="primary" size="sm" :disabled="actionLoading" @click="openCreate">
          New article
        </BaseButton>
      </div>
    </div>

    <section class="mb-6 flex flex-col gap-3 md:flex-row md:items-center">
      <label class="text-xs text-surface-mid">
        Status
        <select
          v-model="statusFilter"
          class="ml-2 rounded-lg border border-surface-border bg-surface-card px-3 py-2 text-surface-light"
        >
          <option value="all">all</option>
          <option value="published">published</option>
          <option value="draft">draft</option>
          <option value="unpublished">unpublished</option>
          <option value="failed">failed</option>
        </select>
      </label>

      <div class="flex flex-wrap gap-2">
        <button
          type="button"
          class="rounded-lg border px-3 py-1.5 text-xs transition-colors"
          :class="
            activeTheme === null
              ? 'border-accent-blue text-accent-blue'
              : 'border-surface-border text-surface-mid hover:border-accent-blue'
          "
          @click="setTheme(null)"
        >
          all themes
        </button>
        <button
          v-for="theme in themes"
          :key="theme"
          type="button"
          class="rounded-lg border px-3 py-1.5 text-xs transition-colors"
          :class="
            activeTheme === theme
              ? 'border-accent-blue text-accent-blue'
              : 'border-surface-border text-surface-mid hover:border-accent-blue'
          "
          @click="setTheme(theme)"
        >
          {{ theme }}
        </button>
      </div>
    </section>

    <section v-if="listLoading" class="space-y-3" aria-busy="true" aria-label="Loading news">
      <div
        v-for="i in 5"
        :key="i"
        class="h-36 rounded-lg border border-surface-border bg-surface-card animate-pulse"
      />
    </section>

    <section
      v-else-if="listError"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
    >
      <p class="text-sm text-surface-mid mb-4">{{ listError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadAdminNews">Retry</BaseButton>
    </section>

    <section v-else-if="articles.length" class="space-y-3">
      <article
        v-for="item in articles"
        :key="item.id"
        class="rounded-lg border border-surface-border bg-surface-card p-5"
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

        <h2 class="card-title mb-2">
          <RouterLink :to="`/news/${item.slug}`" class="hover:text-accent-blue">
            {{ item.title }}
          </RouterLink>
        </h2>
        <p class="text-sm text-surface-mid mb-3">{{ item.summary }}</p>

        <div class="mb-4 flex flex-wrap gap-2">
          <span
            v-for="theme in item.themes"
            :key="theme"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
          >
            {{ theme }}
          </span>
        </div>

        <div class="flex flex-wrap gap-2">
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
            v-if="canWrite"
            variant="ghost"
            size="sm"
            :disabled="actionLoading"
            @click="openEdit(item)"
          >
            Edit
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
          <BaseButton
            v-if="canWrite"
            variant="ghost"
            size="sm"
            :disabled="actionLoading"
            @click="removeArticle(item.id, item.title)"
          >
            Delete
          </BaseButton>
          <a
            :href="item.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center px-3 py-1.5 text-xs text-accent-blue hover:underline"
          >
            Source
          </a>
        </div>
      </article>
    </section>

    <section v-else role="status" class="rounded-lg border border-surface-border bg-surface-card p-8">
      <h2 class="card-title mb-2">No articles</h2>
      <p class="text-sm text-surface-mid">
        No news articles match this filter. Run ingestion after configuring trusted sources.
      </p>
    </section>

    <nav
      v-if="!listLoading && !listError && (articles.length > 0 || page > 1)"
      class="mt-8 flex items-center justify-between"
      aria-label="Admin news pagination"
    >
      <BaseButton variant="ghost" size="sm" :disabled="page <= 1" @click="goToPage(page - 1)">
        Previous
      </BaseButton>
      <span class="text-xs text-surface-muted">page {{ page }}</span>
      <BaseButton variant="ghost" size="sm" :disabled="!hasNextPage" @click="goToPage(page + 1)">
        Next
      </BaseButton>
    </nav>

    <NewsArticleDrawer
      v-if="canWrite"
      :open="drawerOpen"
      :mode="drawerMode"
      :form="form"
      :loading="actionLoading"
      @update:form="form = $event"
      @close="closeDrawer"
      @save="saveDrawer"
    />
  </AdminPageLayout>
</template>
