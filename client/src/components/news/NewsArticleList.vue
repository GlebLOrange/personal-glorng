<script setup lang="ts">
import type { NewsArticle } from "@/types";
import { formatDate } from "@/utils/format";

defineProps<{
  articles: NewsArticle[];
}>();
</script>

<template>
  <div class="space-y-4">
    <article
      v-for="article in articles"
      :key="article.id"
      class="rounded-lg border border-surface-border bg-surface-card p-5 transition-colors hover:border-accent-blue"
    >
      <div class="mb-2 flex flex-wrap items-center gap-2 text-xs text-surface-mid">
        <span class="font-bold text-accent-golden">{{ article.source_name }}</span>
        <span v-for="theme in article.themes" :key="theme">{{ theme }}</span>
        <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
      </div>
      <h2 class="mb-2 text-lg font-bold text-surface-light">
        <a
          :href="article.source_url"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:text-accent-blue"
        >
          {{ article.title }}
        </a>
      </h2>
      <p v-if="article.summary" class="text-sm leading-6 text-surface-sage">
        {{ article.summary }}
      </p>
      <p class="mt-3 text-xs text-surface-muted">
        Created {{ formatDate(article.created_at) }} · Updated {{ formatDate(article.updated_at) }}
      </p>
    </article>
  </div>
</template>
