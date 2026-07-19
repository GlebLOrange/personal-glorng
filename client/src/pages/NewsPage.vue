<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useRouter } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import AdminListFooter from "@/components/admin/AdminListFooter.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import EmptyState from "@/components/ui/EmptyState.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import ListSkeleton from "@/components/ui/ListSkeleton.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, newsArticleDisplayDate, useNews } from "@/composables/useNews";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { safeNavigationHref } from "@/utils/safeUrl";

const router = useRouter();
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
  <PageShell title="news" :breadcrumbs="[{ label: 'news', to: '/news' }]" back-to="/" :narrow="false">
    <div v-if="isSuperuser" class="mb-4 flex min-w-0 items-center">
      <BaseButton
        variant="primary"
        class="ml-auto"
        @click="router.push('/admin/tools/news')"
      >
        manage news
      </BaseButton>
    </div>

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

    <section v-else-if="articles.length" class="min-w-0 space-y-4">
      <Card
        v-for="item in articles"
        :key="item.id"
        as="article"
        variant="compact"
        hoverable
        class="relative min-w-0"
      >
        <RouterLink
          :to="{ name: 'news-article', params: { slug: item.slug } }"
          class="absolute inset-0 z-10 rounded-lg focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent-blue/50"
          :aria-label="item.title"
        />

        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="newsArticleDisplayDate(item)">
            {{ formatNewsDate(newsArticleDisplayDate(item)) }}
          </time>
        </div>

        <h2 class="card-title mb-2 break-words">{{ item.title }}</h2>

        <p class="mb-4 break-words text-sm text-surface-mid">{{ item.summary }}</p>

        <div class="relative z-20 flex flex-wrap items-center gap-2">
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
      @first="goToPage(1)"
      @prev="goToPage(page - 1)"
      @next="goToPage(page + 1)"
      @last="goToPage(totalPages)"
    />
  </PageShell>
</template>
