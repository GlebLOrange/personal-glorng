<script setup lang="ts">
import { onMounted, watch } from "vue";

import BackLink from "@/components/ui/BackLink.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { usePermissions } from "@/composables/usePermissions";

const { isSuperuser } = usePermissions();
const {
  articles,
  page,
  listLoading,
  listError,
  hasNextPage,
  countLabel,
  loadNews,
  goToPage,
} = useNews();

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
      <div
        v-for="i in 5"
        :key="i"
        class="h-40 rounded-lg border border-surface-border bg-surface-card animate-pulse"
      />
    </section>

    <section
      v-else-if="listError"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
    >
      <p class="text-sm text-surface-mid mb-4">{{ listError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadNews">Retry</BaseButton>
    </section>

    <section v-else-if="articles.length" class="space-y-4">
      <article
        v-for="item in articles"
        :key="item.id"
        class="rounded-lg border border-surface-border bg-surface-card p-5"
      >
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
            :href="item.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="ml-auto text-xs text-accent-blue hover:underline"
            @click.stop
          >
            source
          </a>
        </div>
      </article>
    </section>

    <section
      v-else
      role="status"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
    >
      <h2 class="card-title mb-2">No news yet</h2>
      <p class="text-sm text-surface-mid">
        The digest has not published anything yet. Check back after the next ingestion run.
      </p>
    </section>

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
