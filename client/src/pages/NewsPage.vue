<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ListSkeleton from "@/components/ui/ListSkeleton.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, newsArticleDisplayDate, useNews } from "@/composables/useNews";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import type { NewsArticle } from "@/types";

const router = useRouter();

const {
  articles,
  page,
  total,
  totalPages,
  listLoading,
  listError,
  hasNextPage,
  loadNews,
  goToPage,
} = useNews();

useScrollListFingerprint(() => `${page.value}:${total.value}:${articles.value[0]?.id ?? ""}`);

function articleHref(slug: string): string {
  return router.resolve({ name: "news-article", params: { slug } }).href;
}

function cardTitle(item: NewsArticle): string {
  return item.original_title?.trim() || item.title;
}

/** SPA navigate on primary click; keep modifier/middle-click as native href. */
function onArticleClick(event: MouseEvent, slug: string): void {
  if (event.defaultPrevented || event.button !== 0) return;
  if (event.metaKey || event.altKey || event.ctrlKey || event.shiftKey) return;
  event.preventDefault();
  void router.push({ name: "news-article", params: { slug } });
}

onMounted(async () => {
  await loadNews();
});

watch(page, () => {
  void loadNews();
});
</script>

<template>
  <PageShell
    title="news"
    :breadcrumbs="[{ label: 'news', to: '/news' }]"
    back-to="/"
    :narrow="false"
    description="Curated digest from scheduled RSS ingest — each article links back to its source."
  >
    <ListSkeleton
      v-if="listLoading"
      :rows="5"
      label="Loading news"
      row-class="h-40"
      gap-class="space-y-4"
    />

    <ErrorState v-else-if="listError" :message="listError" show-retry @retry="loadNews" />

    <section v-else-if="articles.length" class="min-w-0 space-y-4">
      <Card
        v-for="item in articles"
        :key="item.id"
        as="a"
        :href="articleHref(item.slug)"
        variant="compact"
        hoverable
        class="min-w-0 block"
        :aria-labelledby="`news-card-title-${item.id}`"
        @click="onArticleClick($event, item.slug)"
      >
        <div class="mb-2 flex min-w-0 items-center justify-between gap-2 text-xs text-surface-muted">
          <div class="flex min-w-0 flex-wrap items-center gap-x-2 gap-y-1">
            <span class="shrink-0 text-xs text-accent-coral">
              {{ item.source_name }}
            </span>
            <time
              class="text-datetime shrink-0 whitespace-nowrap lowercase"
              :datetime="newsArticleDisplayDate(item)"
            >
              {{ formatNewsDate(newsArticleDisplayDate(item)) }}
            </time>
          </div>

          <div
            v-if="item.tags.length"
            class="ml-auto flex shrink-0 flex-row-reverse flex-wrap items-center justify-end gap-2"
          >
            <span
              v-for="tag in item.tags"
              :key="tag"
              class="news-tag-chip"
            >
              #{{ tag }}
            </span>
          </div>
        </div>

        <h2
          :id="`news-card-title-${item.id}`"
          class="card-title mb-2 min-w-0 text-balance"
        >
          {{ cardTitle(item) }}
        </h2>

        <p class="break-words text-sm text-surface-mid">{{ item.summary }}</p>
      </Card>
    </section>

    <EmptyState
      v-else
      title="no news yet"
      description="the digest has not published anything yet — check back after the next ingestion run"
    />

    <AdminListFooter
      v-if="!listLoading && !listError && articles.length > 0"
      class="mt-8"
      :total="total"
      :page="page"
      :total-pages="totalPages"
      :has-next-page="hasNextPage"
      :has-previous-page="page > 1"
      :loading="listLoading"
      item-label="articles"
      aria-label="news pagination"
      @first="goToPage(1)"
      @prev="goToPage(page - 1)"
      @next="goToPage(page + 1)"
      @last="goToPage(totalPages)"
    />
  </PageShell>
</template>
