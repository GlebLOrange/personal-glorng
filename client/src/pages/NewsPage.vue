<script setup lang="ts">
import { onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
import { formatNewsDate, useNews } from "@/composables/useNews";

const route = useRoute();
const {
  articles,
  themes,
  activeTheme,
  page,
  listLoading,
  listError,
  hasNextPage,
  countLabel,
  loadNews,
  loadThemes,
  setTheme,
  goToPage,
} = useNews();

onMounted(async () => {
  const theme = Array.isArray(route.query.theme) ? route.query.theme[0] : route.query.theme;
  if (theme) {
    activeTheme.value = String(theme);
  }
  await Promise.all([loadNews(), loadThemes()]);
});

watch([activeTheme, page], () => {
  void loadNews();
});
</script>

<template>
  <main class="max-w-5xl mx-auto px-6 py-12">
    <header class="mb-10">
      <p class="text-label text-surface-mid mb-2">curated from trusted feeds</p>
      <h1 class="section-title mb-3">
        <span class="accent-gradient">news</span>
      </h1>
      <p class="text-body max-w-2xl">
        Short worldwide news summaries with source attribution. Every item links back to the
        original publisher.
      </p>
    </header>

    <section class="mb-8" aria-label="News filters">
      <div class="flex flex-wrap items-center gap-2">
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
          all
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
      <p class="mt-3 text-xs text-surface-muted">{{ countLabel }}</p>
    </section>

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
        class="rounded-lg border border-surface-border bg-surface-card p-5 transition-colors hover:border-accent-blue"
      >
        <div class="mb-3 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ item.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="item.published_at ?? item.created_at">
            {{ formatNewsDate(item.published_at ?? item.created_at) }}
          </time>
        </div>

        <h2 class="card-title mb-2">
          <RouterLink :to="`/news/${item.slug}`" class="hover:text-accent-blue">
            {{ item.title }}
          </RouterLink>
        </h2>

        <p class="text-sm text-surface-mid mb-4">{{ item.summary }}</p>

        <div class="flex flex-wrap items-center gap-2">
          <button
            v-for="theme in item.themes"
            :key="theme"
            type="button"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid hover:border-accent-blue hover:text-accent-blue"
            @click="setTheme(theme)"
          >
            {{ theme }}
          </button>
          <a
            :href="item.source_url"
            target="_blank"
            rel="noopener noreferrer"
            class="ml-auto text-xs text-accent-blue hover:underline"
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
