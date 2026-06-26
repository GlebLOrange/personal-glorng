<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import AdminPageLayout from "@/components/layout/AdminPageLayout.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { usePermissions } from "@/composables/usePermissions";
import type { NewsStatus } from "@/types";

type StatusFilter = NewsStatus | "all";

const statusFilter = ref<StatusFilter>("all");
const { can } = usePermissions();
const canWrite = computed(() => can("news", "write"));

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
  updateArticle,
  deleteArticle,
  repostToTelegram,
} = useNews();

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
      <BaseButton
        v-if="canWrite"
        variant="primary"
        size="sm"
        :disabled="actionLoading"
        @click="runIngest"
      >
        Run ingest
      </BaseButton>
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
  </AdminPageLayout>
</template>
