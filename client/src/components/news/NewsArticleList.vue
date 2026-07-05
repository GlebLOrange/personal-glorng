<script setup lang="ts">
import { Card } from "@/components/ui/card";
import type { NewsArticle } from "@/types";
import { formatDate } from "@/utils/format";
import { safeNavigationHref } from "@/utils/safeUrl";

defineProps<{
  articles: NewsArticle[];
}>();
</script>

<template>
  <div class="space-y-4">
    <Card
      v-for="article in articles"
      :key="article.id"
      as="article"
      variant="compact"
      hoverable
    >
      <div class="mb-2 flex flex-wrap items-center gap-2 text-xs text-surface-mid">
        <span class="font-bold text-accent-golden">{{ article.source_name }}</span>
        <span v-for="theme in article.themes" :key="theme">{{ theme }}</span>
        <span v-if="article.published_at">{{ formatDate(article.published_at) }}</span>
      </div>
      <h2 class="mb-2 text-lg font-bold text-surface-light">
        <a
          v-if="safeNavigationHref(article.source_url)"
          :href="safeNavigationHref(article.source_url) ?? '#'"
          target="_blank"
          rel="noopener noreferrer"
          class="hover:text-accent-blue"
        >
          {{ article.title }}
        </a>
        <span v-else>{{ article.title }}</span>
      </h2>
      <p v-if="article.summary" class="text-sm leading-6 text-surface-sage">
        {{ article.summary }}
      </p>
      <p class="mt-3 text-xs text-surface-muted">
        Created {{ formatDate(article.created_at) }} · Updated {{ formatDate(article.updated_at) }}
      </p>
    </Card>
  </div>
</template>
