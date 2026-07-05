<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import BackLink from "@/components/ui/BackLink.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, useNews } from "@/composables/useNews";
import { safeNavigationHref } from "@/utils/safeUrl";

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
    <BackLink to="/news" class="mb-8" />

    <Card
      v-if="detailLoading"
      class="h-96 animate-pulse"
      aria-busy="true"
      aria-label="Loading article"
    />

    <Card v-else-if="detailError" as="section" class="!p-8 text-center">
      <p class="text-sm text-surface-mid mb-4">{{ detailError }}</p>
      <BaseButton variant="ghost" size="sm" @click="loadCurrentArticle">Retry</BaseButton>
    </Card>

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
          <Card
            v-for="bullet in article.bullets"
            :key="bullet"
            as="li"
            variant="compact"
          >
            {{ bullet }}
          </Card>
        </ul>
      </section>

      <section class="mb-8">
        <h2 class="card-title mb-4">Themes</h2>
        <div class="flex flex-wrap gap-2">
          <span
            v-for="theme in article.themes"
            :key="theme"
            class="rounded border border-surface-border px-2 py-1 text-xs text-surface-mid"
          >
            {{ theme }}
          </span>
        </div>
      </section>

      <Card as="footer" variant="compact">
        <p class="text-sm text-surface-mid mb-3">
          This is a curated summary. Read the original article from
          {{ article.source_name }} for full context.
        </p>
        <a
          v-if="safeNavigationHref(article.source_url)"
          :href="safeNavigationHref(article.source_url) ?? '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="text-sm text-accent-blue hover:underline"
        >
          Open original source
        </a>
      </Card>
    </article>
  </main>
</template>
