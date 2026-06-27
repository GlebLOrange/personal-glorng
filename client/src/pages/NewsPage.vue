<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";

import NewsArticleList from "@/components/news/NewsArticleList.vue";
import TaskPagination from "@/components/tasks/TaskPagination.vue";
import BaseButton from "@/components/ui/BaseButton.vue";
import BaseSelect from "@/components/ui/BaseSelect.vue";
import { useCachedApi } from "@/composables/useCachedApi";
import type { NewsListResponse } from "@/types";
import { formatDate } from "@/utils/format";

const LATEST_NEWS_LIMIT = 20;
type NewsSort =
  | "published_at:desc"
  | "published_at:asc"
  | "created_at:desc"
  | "created_at:asc"
  | "updated_at:desc"
  | "updated_at:asc";

const selectedSource = ref("all");
const selectedCategory = ref("all");
const selectedRegion = ref("all");
const selectedSort = ref<NewsSort>("published_at:desc");
const page = ref(1);
const error = ref(false);

const apiUrl = computed(() => {
  const params = new URLSearchParams({
    page: String(page.value),
    per_page: String(LATEST_NEWS_LIMIT),
  });
  const [sortBy, sortOrder] = selectedSort.value.split(":");
  if (selectedSource.value !== "all") params.set("source", selectedSource.value);
  if (selectedCategory.value !== "all") params.set("category", selectedCategory.value);
  if (selectedRegion.value !== "all") params.set("region", selectedRegion.value);
  params.set("sort_by", sortBy);
  params.set("sort_order", sortOrder);
  return `/news?${params.toString()}`;
});

const { data: news, loading, fetch } = useCachedApi<NewsListResponse>(apiUrl, 120_000);
const articles = computed(() => news.value?.articles ?? []);
const hasNextPage = computed(() => page.value < (news.value?.pages ?? 0));

const hasFilters = computed(
  () =>
    selectedSource.value !== "all" ||
    selectedCategory.value !== "all" ||
    selectedRegion.value !== "all" ||
    selectedSort.value !== "published_at:desc",
);
const hasNoNews = computed(
  () => !loading.value && !error.value && !hasFilters.value && articles.value.length === 0,
);

async function loadNews(): Promise<void> {
  error.value = false;
  try {
    await fetch();
  } catch (err) {
    if (import.meta.env.DEV) console.error(err);
    error.value = true;
  }
}

function clearFilters(): void {
  selectedSource.value = "all";
  selectedCategory.value = "all";
  selectedRegion.value = "all";
  selectedSort.value = "published_at:desc";
  page.value = 1;
}

async function goToPage(nextPage: number): Promise<void> {
  page.value = Math.max(1, nextPage);
  await loadNews();
}

onMounted(loadNews);
watch(
  [selectedSource, selectedCategory, selectedRegion, selectedSort],
  async () => {
    page.value = 1;
    await loadNews();
  },
  { deep: true },
);
</script>

<template>
  <div class="mx-auto max-w-5xl px-6 py-10">
    <div v-if="!hasNoNews" class="mb-8">
      <p class="mb-2 text-label text-accent-golden">worldwide rss</p>
      <h1 class="mb-3 text-3xl font-bold accent-gradient">news</h1>
      <p class="max-w-2xl text-sm leading-6 text-surface-mid">
        A lightweight feed of headlines parsed from admin-managed RSS sources around the world.
      </p>
      <p v-if="news?.updated_at" class="mt-3 text-xs text-surface-muted">
        Updated {{ formatDate(news.updated_at) }} · {{ news.total }} articles
      </p>
    </div>

    <div v-if="!hasNoNews" class="mb-6 space-y-3">
      <div class="grid grid-cols-1 gap-3 md:grid-cols-4">
        <BaseSelect v-model="selectedSource" label="Source">
          <option value="all">All sources</option>
          <option v-for="source in news?.sources ?? []" :key="source" :value="source">
            {{ source }}
          </option>
        </BaseSelect>
        <BaseSelect v-model="selectedCategory" label="Category">
          <option value="all">All categories</option>
          <option v-for="category in news?.categories ?? []" :key="category" :value="category">
            {{ category }}
          </option>
        </BaseSelect>
        <BaseSelect v-model="selectedRegion" label="Region">
          <option value="all">All regions</option>
          <option v-for="region in news?.regions ?? []" :key="region" :value="region">
            {{ region }}
          </option>
        </BaseSelect>
        <BaseSelect v-model="selectedSort" label="Sort">
          <option value="published_at:desc">Published newest</option>
          <option value="published_at:asc">Published oldest</option>
          <option value="created_at:desc">Created newest</option>
          <option value="created_at:asc">Created oldest</option>
          <option value="updated_at:desc">Updated newest</option>
          <option value="updated_at:asc">Updated oldest</option>
        </BaseSelect>
      </div>
      <div class="flex justify-end rounded-lg border border-surface-border p-3">
        <BaseButton variant="ghost" :disabled="!hasFilters" @click="clearFilters">
          Clear filters
        </BaseButton>
      </div>
    </div>

    <div v-if="loading" class="space-y-4" aria-busy="true" aria-label="Loading news">
      <div
        v-for="i in 6"
        :key="i"
        class="h-32 animate-pulse rounded-lg border border-surface-border bg-surface-card"
      />
    </div>

    <div
      v-else-if="error"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
      role="status"
    >
      <p class="mb-4 text-sm text-surface-mid">News is unavailable right now.</p>
      <BaseButton variant="ghost" size="sm" @click="loadNews">Retry</BaseButton>
    </div>

    <div
      v-else-if="hasNoNews"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
      role="status"
    >
      <p class="text-sm text-accent-golden">No news articles available yet.</p>
    </div>

    <div
      v-else-if="articles.length === 0"
      class="rounded-lg border border-surface-border bg-surface-card p-8 text-center"
      role="status"
    >
      <p class="mb-4 text-sm text-surface-mid">No articles match those filters.</p>
      <BaseButton variant="ghost" size="sm" @click="clearFilters">Clear filters</BaseButton>
    </div>

    <template v-else>
      <NewsArticleList :articles="articles" />
      <TaskPagination
        v-if="news && (news.pages > 1 || page > 1)"
        :page="page"
        :has-next-page="hasNextPage"
        @prev="goToPage(page - 1)"
        @next="goToPage(page + 1)"
      />
    </template>
  </div>
</template>
