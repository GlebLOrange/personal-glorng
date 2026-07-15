import { computed, ref } from "vue";

import { LIST_PAGE_SIZE } from "@/constants/pagination";
import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import type {
  NewsArticle,
  NewsArticleCreate,
  NewsArticleMetadata,
  NewsArticleUpdate,
  NewsIngestResult,
  NewsSource,
  NewsStatus,
  PaginatedNews,
} from "@/types";

export interface NewsStats {
  total: number;
  draft: number;
  published: number;
  unpublished: number;
  failed: number;
}

export function formatNewsDate(value: string | null): string {
  if (!value) return "not published";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function newsArticleDisplayDate(article: NewsArticle): string {
  return article.source_published_at ?? article.published_at ?? article.created_at;
}

export function useNews() {
  const articles = ref<NewsArticle[]>([]);
  const article = ref<NewsArticle | null>(null);
  const sources = ref<NewsSource[]>([]);
  const newsStats = ref<NewsStats | null>(null);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);

  const { loading: listLoading, lastError: listError, run: runList } = useApiAction();
  const { loading: statsLoading, run: runStats } = useApiAction();
  const { loading: detailLoading, lastError: detailError, run: runDetail } = useApiAction();
  const { loading: actionLoading, run: runAction } = useApiAction();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const hasPreviousPage = computed(() => page.value > 1);
  const countLabel = computed(() => {
    return `${total.value} article${total.value === 1 ? "" : "s"}`;
  });

  async function loadNews(options: { admin?: boolean; status?: NewsStatus | null } = {}) {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: LIST_PAGE_SIZE,
    };
    if (options.status) params.status = options.status;
    const endpoint = options.admin ? "/tools/news/admin" : "/tools/news";
    const data = await runList(
      async () => {
        const response = await api.get<PaginatedNews>(endpoint, { params });
        return response.data;
      },
      { errorFallback: "Failed to load news", logContext: "news.loadList" },
    );
    if (data) {
      articles.value = data.items;
      total.value = data.total;
      totalPages.value = data.pages;
    }
  }

  async function loadNewsStats(): Promise<void> {
    const data = await runStats(
      async () => {
        const response = await api.get<NewsStats>("/tools/news/admin/stats");
        return response.data;
      },
      { errorFallback: "Failed to load news stats", logContext: "news.loadStats" },
    );
    if (data) newsStats.value = data;
  }

  async function loadArticle(slug: string): Promise<void> {
    const data = await runDetail(
      async () => {
        const response = await api.get<NewsArticle>(`/tools/news/${slug}`);
        return response.data;
      },
      { errorFallback: "Failed to load article", logContext: "news.loadArticle" },
    );
    article.value = data ?? null;
  }

  async function loadAdminArticle(articleId: number): Promise<void> {
    const data = await runDetail(
      async () => {
        const response = await api.get<NewsArticle>(`/tools/news/admin/${articleId}`);
        return response.data;
      },
      { errorFallback: "Failed to load article", logContext: "news.loadAdminArticle" },
    );
    article.value = data ?? null;
  }

  async function loadSources(): Promise<void> {
    const data = await runAction(
      async () => {
        const response = await api.get<NewsSource[]>("/tools/news-sources");
        return response.data;
      },
      { errorFallback: "Failed to load news sources", logContext: "news.loadSources" },
    );
    if (data) sources.value = data;
  }

  function goToPage(nextPage: number): void {
    if (nextPage < 1) return;
    if (totalPages.value > 0 && nextPage > totalPages.value) return;
    page.value = nextPage;
  }

  async function ingestNews(): Promise<NewsIngestResult | undefined> {
    return runAction(
      async () => {
        const response = await api.post<NewsIngestResult>("/tools/news/ingest");
        return response.data;
      },
      { successMessage: "News ingest started", errorFallback: "Failed to ingest news" },
    );
  }

  async function loadArticleMetadata(url: string): Promise<NewsArticleMetadata | undefined> {
    return runAction(
      async () => {
        const response = await api.post<NewsArticleMetadata>("/tools/news/metadata", { url });
        return response.data;
      },
      {
        errorFallback: "Failed to load article metadata",
        logContext: "news.loadArticleMetadata",
      },
    );
  }

  async function updateArticle(
    articleId: number,
    payload: NewsArticleUpdate,
  ): Promise<NewsArticle | undefined> {
    return runAction(
      async () => {
        const response = await api.put<NewsArticle>(`/tools/news/${articleId}`, payload);
        return response.data;
      },
      { successMessage: "News article updated", errorFallback: "Failed to update article" },
    );
  }

  async function createArticle(payload: NewsArticleCreate): Promise<NewsArticle | undefined> {
    return runAction(
      async () => {
        const response = await api.post<NewsArticle>("/tools/news", payload);
        return response.data;
      },
      { successMessage: "News article created", errorFallback: "Failed to create article" },
    );
  }

  async function deleteArticle(articleId: number): Promise<boolean> {
    const result = await runAction(
      async () => {
        await api.delete(`/tools/news/${articleId}`);
        return true;
      },
      { successMessage: "News article deleted", errorFallback: "Failed to delete article" },
    );
    return Boolean(result);
  }

  async function repostToTelegram(articleId: number): Promise<NewsArticle | undefined> {
    return runAction(
      async () => {
        const response = await api.post<NewsArticle>(`/tools/news/${articleId}/telegram`);
        return response.data;
      },
      { successMessage: "Posted to Telegram", errorFallback: "Failed to post to Telegram" },
    );
  }

  return {
    articles,
    article,
    sources,
    newsStats,
    page,
    total,
    totalPages,
    listLoading,
    listError,
    statsLoading,
    detailLoading,
    detailError,
    actionLoading,
    hasNextPage,
    hasPreviousPage,
    countLabel,
    loadNews,
    loadNewsStats,
    loadArticle,
    loadAdminArticle,
    loadSources,
    goToPage,
    ingestNews,
    loadArticleMetadata,
    createArticle,
    updateArticle,
    deleteArticle,
    repostToTelegram,
  };
}
