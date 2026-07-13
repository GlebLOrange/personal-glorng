<script setup lang="ts">
import { onMounted, watch } from "vue";

import PageShell from "@/components/layout/PageShell.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { usePermissions } from "@/composables/usePermissions";
import { useScrollListFingerprint } from "@/composables/useScrollListFingerprint";
import { safeNavigationHref } from "@/utils/safeUrl";

const { isSuperuser } = usePermissions();
const { articles, page, total, listLoading, listError, hasNextPage, countLabel, loadNews, goToPage } =
  useNews();

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
      <div class="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-surface-muted">
        <span>{{ countLabel }}</span>
        <RouterLink
          v-if="isSuperuser"
          to="/admin/tools/news"
          class="text-accent-blue hover:underline"
        >
          Manage news
        </RouterLink>
      </div>
    </header>

    <section v-if="listLoading" class="space-y-4" aria-busy="true" aria-label="Loading news">
      <Card v-for="i in 5" :key="i" class="h-40 animate-pulse" />
    </section>

    <Card v-else-if="listError" as="section" class="!p-8 text-center">
      <p class="text-sm text-surface-mid mb-4">{{ listError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadNews">Retry</BaseButton>
    </Card>

    <section v-else-if="articles.length" class="space-y-4 min-w-0">
      <Card v-for="item in articles" :key="item.id" as="article" variant="compact" class="min-w-0">
        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="item.published_at ?? item.created_at">
            {{ formatNewsDate(item.published_at ?? item.created_at) }}
          </time>
        </div>

        <h2 class="card-title mb-2 break-words">{{ item.title }}</h2>

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

    <Card v-else as="section" role="status" class="!p-8 text-center">
      <h2 class="card-title mb-2">No news yet</h2>
      <p class="text-sm text-surface-mid">
        The digest has not published anything yet. Check back after the next ingestion run.
      </p>
    </Card>

    <nav
      v-if="!listLoading && !listError && (articles.length > 0 || page > 1)"
      class="mt-8 flex items-center justify-between"
      aria-label="News pagination"
    >
      <BaseButton variant="ghost" size="sm" :disabled="page <= 1" @click="goToPage(page - 1)">
        Previous
      </BaseButton>
      <span class="text-xs text-surface-muted">page {{ page }}</span>
      <BaseButton variant="ghost" size="sm" :disabled="!hasNextPage" @click="goToPage(page + 1)">
        Next
      </BaseButton>
    </nav>
  </PageShell>
</template>
