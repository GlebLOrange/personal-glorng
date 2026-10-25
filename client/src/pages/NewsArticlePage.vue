<script setup lang="ts">
import { computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";

import PageShell from "@/components/layout/PageShell.vue";
import type { BreadcrumbSegment } from "@/components/layout/PageShell.vue";
import ErrorState from "@/components/ui/ErrorState.vue";
import FieldHelp from "@/components/ui/FieldHelp.vue";
import { Card } from "@/components/ui/card";
import { formatNewsDate, newsArticleDisplayDate, useNews } from "@/composables/useNews";
import { applyPageSeo } from "@/utils/pageSeo";
import { formatEmbeddedDates, truncateBreadcrumbSlug } from "@/utils/format";
import { safeNavigationHref } from "@/utils/safeUrl";

const route = useRoute();
const slug = computed(() => String(route.params.slug ?? ""));
const crumbSlug = computed(() => truncateBreadcrumbSlug(slug.value));

const { article, detailLoading, detailError, loadArticle } = useNews();

const articleTitle = computed(() => article.value?.title ?? "article");
const breadcrumbs = computed((): BreadcrumbSegment[] => {
  const trail: BreadcrumbSegment[] = [{ label: "news", to: "/news" }];
  const crumbLabel = article.value?.title?.trim() || crumbSlug.value;
  if (crumbLabel) trail.push({ label: crumbLabel });
  return trail;
});
/** Drop publish-date bullets — header already shows newsArticleDisplayDate. */
const keyPoints = computed(() =>
  (article.value?.bullets ?? []).filter((bullet) => !/^Published:\s/i.test(bullet.trim())),
);

async function loadCurrentArticle(): Promise<void> {
  if (slug.value) {
    await loadArticle(slug.value);
  }
}

onMounted(loadCurrentArticle);
watch(slug, () => {
  void loadCurrentArticle();
});

watch(
  article,
  (value) => {
    if (!value) return;
    applyPageSeo({
      title: value.title,
      description: value.summary || undefined,
      path: `/news/${value.slug}`,
    });
  },
  { immediate: true },
);
</script>

<template>
  <PageShell
    :title="articleTitle"
    :breadcrumbs="breadcrumbs"
    back-to="/news"
    :narrow="false"
    omit-heading
  >
    <Card
      v-if="detailLoading"
      class="h-96 animate-pulse"
      aria-busy="true"
      aria-label="loading article"
    />

    <ErrorState
      v-else-if="detailError"
      :message="detailError"
      show-retry
      @retry="loadCurrentArticle"
    />

    <article v-else-if="article" class="min-w-0 w-full">
      <header class="mb-8 min-w-0">
        <h1
          class="mb-4 text-2xl font-semibold text-surface-light text-balance break-words md:text-3xl"
        >
          {{ article.title }}
        </h1>
        <div class="mb-4 flex w-full min-w-0 flex-wrap items-center gap-x-4 gap-y-2 text-xs text-surface-muted">
          <div class="flex min-w-0 flex-wrap items-center gap-2">
            <a
              v-if="safeNavigationHref(article.source_url)"
              :href="safeNavigationHref(article.source_url) ?? '#'"
              target="_blank"
              rel="noopener noreferrer"
              title="source"
              class="shrink-0 text-accent-coral hover:underline"
            >
              {{ article.source_name }}
            </a>
            <span v-else class="shrink-0 text-accent-coral">{{ article.source_name }}</span>
            <time class="shrink-0 text-left" :datetime="newsArticleDisplayDate(article)">
              {{ formatNewsDate(newsArticleDisplayDate(article)) }}
            </time>
            <FieldHelp
              :text="`this is a curated summary — read the original article from ${article.source_name} for full context`"
            />
          </div>
          <ul
            v-if="article.tags.length"
            class="m-0 ml-auto flex list-none flex-row-reverse flex-wrap justify-end gap-2 p-0"
            aria-label="tags"
          >
            <li
              v-for="tag in article.tags"
              :key="tag"
              class="news-tag-chip"
            >
              #{{ tag }}
            </li>
          </ul>
        </div>
        <p class="text-body break-words">{{ article.summary }}</p>
      </header>

      <section v-if="keyPoints.length" class="mb-8 min-w-0">
        <h2 class="card-title mb-4">key points</h2>
        <ul class="min-w-0 space-y-3 text-sm text-surface-mid">
          <li
            v-for="bullet in keyPoints"
            :key="bullet"
            class="break-words border-l-2 border-accent-coral/40 pl-3 text-body"
          >
            {{ formatEmbeddedDates(bullet) }}
          </li>
        </ul>
      </section>
    </article>
  </PageShell>
</template>
