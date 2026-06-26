<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import BaseButton from "@/components/ui/BaseButton.vue";
import { formatNewsDate, useNews } from "@/composables/useNews";

const route = useRoute();
const slug = computed(() => String(route.params.slug ?? ""));

const { article, detailLoading, detailError, loadArticle } = useNews();

async function loadCurrentArticle(): Promise<void> {
  if (slug.value) {
    await loadArticle(slug.value);
  }
}

onMounted(loadCurrentArticle);
watch(slug, () => {
  void loadCurrentArticle();
});
</script>

<template>
  <main class="max-w-3xl mx-auto px-6 py-12">
    <RouterLink to="/news" class="nav-link-accent mb-8 inline-flex text-sm">
      Back to news
    </RouterLink>

    <div
      v-if="detailLoading"
      class="h-96 rounded-lg border border-surface-border bg-surface-card animate-pulse"
      aria-busy="true"
      aria-label="Loading article"
    />

    <section
      v-else-if="detailError"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
    >
      <p class="text-sm text-surface-mid mb-4">{{ detailError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadCurrentArticle">Retry</BaseButton>
    </section>

    <article v-else-if="article">
      <header class="mb-8">
        <div class="mb-4 flex flex-wrap items-center gap-2 text-xs text-surface-muted">
          <span>{{ article.source_name }}</span>
          <span aria-hidden="true">/</span>
          <time :datetime="article.published_at ?? article.created_at">
            {{ formatNewsDate(article.published_at ?? article.created_at) }}
          </time>
        </div>
        <h1 class="section-title mb-4">{{ article.title }}</h1>
        <p class="text-body">{{ article.summary }}</p>
      </header>

      <section v-if="article.bullets.length" class="mb-8">
        <h2 class="card-title mb-4">Key points</h2>
        <ul class="space-y-3 text-sm text-surface-mid">
          <li
            v-for="bullet in article.bullets"
            :key="bullet"
            class="rounded-lg border border-surface-border bg-surface-card p-4"
          >
            {{ bullet }}
          </li>
        </ul>
      </section>

      <section class="mb-8">
        <h2 class="card-title mb-4">Themes</h2>
        <div class="flex flex-wrap gap-2">
          <RouterLink
            v-for="theme in article.themes"
            :key="theme"
            :to="{ path: '/news', query: { theme } }"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid hover:border-accent-blue hover:text-accent-blue"
          >
            {{ theme }}
          </RouterLink>
        </div>
      </section>

      <footer class="rounded-lg border border-surface-border bg-surface-card p-5">
        <p class="text-sm text-surface-mid mb-3">
          This is a curated summary. Read the original article from
          {{ article.source_name }} for full context.
        </p>
        <a
          :href="article.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="text-sm text-accent-blue hover:underline"
        >
          Open original source
        </a>
      </footer>
    </article>
  </main>
</template>
