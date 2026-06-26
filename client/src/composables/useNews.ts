import { computed, ref } from "vue";

import { api } from "@/composables/useApi";
import { useApiAction } from "@/composables/useApiAction";
import type {
  NewsArticle,
  NewsArticleCreate,
  NewsArticleUpdate,
  NewsIngestResult,
  NewsStatus,
  PaginatedNews,
} from "@/types";

const PER_PAGE = 20;

export function formatNewsDate(value: string | null): string {
  if (!value) return "not published";
  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function useNews() {
  const articles = ref<NewsArticle[]>([]);
  const article = ref<NewsArticle | null>(null);
  const themes = ref<string[]>([]);
  const activeTheme = ref<string | null>(null);
  const page = ref(1);
  const total = ref(0);
  const totalPages = ref(0);

  const { loading: listLoading, lastError: listError, run: runList } = useApiAction();
  const { loading: detailLoading, lastError: detailError, run: runDetail } = useApiAction();
  const { loading: actionLoading, run: runAction } = useApiAction();
  const { run: runThemes } = useApiAction();

  const hasNextPage = computed(() => page.value < totalPages.value);
  const countLabel = computed(() => {
    const label = `${total.value} article${total.value === 1 ? "" : "s"}`;
    return activeTheme.value ? `${label} in ${activeTheme.value}` : label;
  });

  async function loadNews(options: { admin?: boolean; status?: NewsStatus | null } = {}) {
    const params: Record<string, string | number> = {
      page: page.value,
      per_page: PER_PAGE,
    };
    if (activeTheme.value) params.theme = activeTheme.value;
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

  async function loadThemes(): Promise<void> {
    const data = await runThemes(
      async () => {
        const response = await api.get<string[]>("/tools/news/themes");
        return response.data;
      },
      { errorFallback: "Failed to load themes", silent: true, logContext: "news.loadThemes" },
    );
    if (data) themes.value = data;
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

  function setTheme(theme: string | null): void {
    activeTheme.value = activeTheme.value === theme ? null : theme;
    page.value = 1;
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
    themes,
    activeTheme,
    page,
    total,
    totalPages,
    listLoading,
    listError,
    detailLoading,
    detailError,
    actionLoading,
    hasNextPage,
    countLabel,
    loadNews,
    loadThemes,
    loadArticle,
    setTheme,
    goToPage,
    ingestNews,
    createArticle,
    updateArticle,
    deleteArticle,
    repostToTelegram,
  };
}
