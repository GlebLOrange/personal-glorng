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
import { truncateBreadcrumbSlug } from "@/utils/format";
import { safeNavigationHref } from "@/utils/safeUrl";

const route = useRoute();
const slug = computed(() => String(route.params.slug ?? ""));
const crumbSlug = computed(() => truncateBreadcrumbSlug(slug.value));

const { article, detailLoading, detailError, loadArticle } = useNews();

const articleTitle = computed(() => article.value?.title ?? "article");
const breadcrumbs = computed((): BreadcrumbSegment[] => {
  const trail: BreadcrumbSegment[] = [{ label: "news", to: "/news" }];
  if (crumbSlug.value) trail.push({ label: crumbSlug.value });
  return trail;
});

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
      path: route.fullPath,
    });
  },
  { immediate: true },
);
</script>

<template>
  <PageShell :title="articleTitle" :breadcrumbs="breadcrumbs" back-to="/news" :narrow="false">
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
        <div
          class="mb-4 flex w-full min-w-0 flex-wrap items-center justify-between gap-2 text-xs text-surface-muted"
        >
          <time class="shrink-0 text-left" :datetime="newsArticleDisplayDate(article)">
            {{ formatNewsDate(newsArticleDisplayDate(article)) }}
          </time>
          <div class="flex shrink-0 items-center gap-2">
            <a
              v-if="safeNavigationHref(article.source_url)"
              :href="safeNavigationHref(article.source_url) ?? '#'"
              target="_blank"
              rel="noopener noreferrer"
              title="source"
              class="text-accent-blue hover:underline"
            >
              {{ article.source_name }}
            </a>
            <span v-else class="text-accent-blue">{{ article.source_name }}</span>
            <FieldHelp
              align="end"
              :text="`this is a curated summary. read the original article from ${article.source_name} for full context.`"
            />
          </div>
        </div>
        <p class="text-body break-words">{{ article.summary }}</p>
      </header>

      <section v-if="article.bullets.length" class="mb-8 min-w-0">
        <h2 class="card-title mb-4">key points</h2>
        <ul class="min-w-0 space-y-3 text-sm text-surface-mid">
          <li
            v-for="bullet in article.bullets"
            :key="bullet"
            class="break-words border-l-2 border-accent-blue/40 pl-3 text-body"
          >
            {{ bullet }}
          </li>
        </ul>
      </section>

      <section v-if="article.tags.length" class="mb-8 min-w-0">
        <h2 class="card-title mb-4">tags</h2>
        <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
          <li
            v-for="tag in article.tags"
            :key="tag"
            class="rounded bg-accent-blue/10 px-2.5 py-1 text-xs text-accent-blue"
          >
            #{{ tag }}
          </li>
        </ul>
      </section>
    </article>
  </PageShell>
</template>
