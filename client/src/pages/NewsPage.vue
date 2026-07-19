<script setup lang="ts">
import { onMounted, watch } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ListSkeleton from "@/components/ui/ListSkeleton.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, newsArticleDisplayDate, useNews } from "@/composables/useNews";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { safeNavigationHref } from "@/utils/safeUrl";

const { isSuperuser } = usePermissions();
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

useScrollListFingerprint(
  () => `${page.value}:${total.value}:${articles.value[0]?.id ?? ""}`,
);

onMounted(async () => {
  await loadNews();
});

watch(page, () => {
  void loadNews();
});
</script>

<template>
  <PageShell title="news" :breadcrumbs="[{ label: 'news' }]">
    <header class="page-intro">
      <p class="text-label text-surface-mid mb-2">curated from trusted feeds</p>
      <p class="text-body">
        Short worldwide news summaries with source attribution. Every item links back to the
        original publisher.
      </p>
      <div v-if="isSuperuser" class="mt-3">
        <RouterLink to="/admin/tools/news" class="text-xs text-accent-blue hover:underline">
          manage news
        </RouterLink>
      </div>
    </header>

    <ListSkeleton
      v-if="listLoading"
      :rows="5"
      label="Loading news"
      row-class="h-40"
      gap-class="space-y-4"
    />

    <ErrorState
      v-else-if="listError"
      :message="listError"
      show-retry
      @retry="loadNews"
    />

    <section v-else-if="articles.length" class="space-y-4 min-w-0">
      <Card v-for="item in articles" :key="item.id" as="article" variant="compact" class="min-w-0">
        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="newsArticleDisplayDate(item)">
            {{ formatNewsDate(newsArticleDisplayDate(item)) }}
          </time>
        </div>

        <h2 class="card-title mb-2 break-words">
          <RouterLink
            :to="{ name: 'news-article', params: { slug: item.slug } }"
            class="hover:text-accent-blue transition-colors"
          >
            {{ item.title }}
          </RouterLink>
        </h2>

        <p class="text-sm text-surface-mid mb-4 break-words">{{ item.summary }}</p>

        <div class="flex flex-wrap items-center gap-2">
          <span
            v-for="theme in item.themes"
            :key="theme"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
          >
            {{ theme }}
          </span>
          <a
            v-if="safeNavigationHref(item.source_url)"
            :href="safeNavigationHref(item.source_url) ?? '#'"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs text-accent-blue hover:underline"
            @click.stop
          >
            source
          </a>
        </div>
      </Card>
    </section>

    <EmptyState
      v-else
      title="No news yet"
      description="The digest has not published anything yet. Check back after the next ingestion run."
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
      ariaLabel="News pagination"
      @prev="goToPage(page - 1)"
      @next="goToPage(page + 1)"
    />
  </PageShell>
</template>
