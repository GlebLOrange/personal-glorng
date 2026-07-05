<script setup lang="ts">
import { onMounted, watch } from "vue";

import BackLink from "@/components/ui/BackLink.vue";
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
  <main class="max-w-5xl mx-auto px-6 py-12">
    <header class="mb-10">
      <p class="text-label text-surface-mid mb-2">curated from trusted feeds</p>
      <div class="mb-3 flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <h1 class="section-title">
          <span class="accent-gradient">news</span>
        </h1>
        <BackLink to="/tools" />
      </div>
      <div class="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="text-body max-w-2xl">
            Short worldwide news summaries with source attribution. Every item links back to the
            original publisher.
          </p>
          <p class="mt-3 text-xs text-surface-muted">{{ countLabel }}</p>
        </div>
        <RouterLink
          v-if="isSuperuser"
          to="/admin/tools/news"
          class="text-xs text-accent-blue hover:underline"
        >
          Manage news
        </RouterLink>
      </div>
    </header>

    <section v-if="listLoading" class="space-y-4" aria-busy="true" aria-label="Loading news">
      <Card v-for="i in 5" :key="i" class="h-40 animate-pulse" />
    </section>

    <Card
      v-else-if="listError"
      as="section"
      class="!p-8 text-center"
    >
      <p class="text-sm text-surface-mid mb-4">{{ listError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadNews">Retry</BaseButton>
    </Card>

    <section v-else-if="articles.length" class="space-y-4">
      <Card v-for="item in articles" :key="item.id" as="article" variant="compact">
        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="item.published_at ?? item.created_at">
            {{ formatNewsDate(item.published_at ?? item.created_at) }}
          </time>
        </div>

        <h2 class="card-title mb-2">{{ item.title }}</h2>

        <p class="text-sm text-surface-mid mb-4">{{ item.summary }}</p>

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
            class="ml-auto text-xs text-accent-blue hover:underline"
            @click.stop
          >
            source
          </a>
        </div>
      </Card>
    </section>

    <Card
      v-else
      as="section"
      role="status"
      class="!p-8 text-center"
    >
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
  </main>
</template>
