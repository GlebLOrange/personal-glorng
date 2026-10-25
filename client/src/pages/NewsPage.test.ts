import { flushPromises, mount } from "@vue/test-utils";
import { computed, ref } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import NewsPage from "@/pages/NewsPage.vue";
import type { NewsArticle } from "@/types";

const articles = ref<NewsArticle[]>([]);
const listLoading = ref(false);
const listError = ref<string | null>(null);
const page = ref(1);
const total = ref(0);
const totalPages = ref(0);
const loadNews = vi.fn(async () => undefined);
const goToPage = vi.fn();

vi.mock("@/composables/useNews", () => ({
  formatNewsDate: (value: string | null) => value ?? "",
  newsArticleDisplayDate: (article: NewsArticle) =>
    article.published_at ?? article.created_at,
  useNews: () => ({
    articles,
    page,
    total,
    totalPages,
    listLoading,
    listError,
    hasNextPage: computed(() => page.value < totalPages.value),
    loadNews,
    goToPage,
  }),
}));

vi.mock("@/composables/useScrollListFingerprint", () => ({
  useScrollListFingerprint: () => undefined,
}));

const routerPush = vi.fn();

vi.mock("vue-router", () => ({
  useRouter: () => ({
    resolve: (to: { params?: { slug?: string } } | string) => ({
      href:
        typeof to === "string"
          ? to
          : to?.params?.slug
            ? `/news/${to.params.slug}`
            : "#",
    }),
    push: routerPush,
  }),
}));

const sampleArticle: NewsArticle = {
  id: 1,
  slug: "sample-article",
  status: "published",
  source_id: 1,
  source_name: "Example Source",
  source_url: "https://example.com/article",
  source_feed_url: "https://example.com/feed",
  source_published_at: "2026-01-02T00:00:00Z",
  original_title: "Original",
  title: "Scan-friendly title",
  summary: "A concise summary for hiring managers.",
  bullets: [],
  tags: ["python", "fastapi"],
  language: "en",
  published_at: "2026-01-02T12:00:00Z",
  telegram_message_id: null,
  ai_model: null,
  ai_input_hash: null,
  ingest_error: null,
  created_at: "2026-01-01T00:00:00Z",
  updated_at: "2026-01-02T12:00:00Z",
};

function mountPage() {
  return mount(NewsPage, {
    global: {
      stubs: {
        PageShell: {
          props: ["title", "breadcrumbs", "backTo", "narrow", "description"],
          template: "<div><slot /></div>",
        },
        AdminListFooter: true,
      },
    },
  });
}

describe("NewsPage card order", () => {
  beforeEach(() => {
    articles.value = [];
    listLoading.value = false;
    listError.value = null;
    page.value = 1;
    total.value = 0;
    totalPages.value = 0;
    loadNews.mockClear();
    goToPage.mockClear();
    routerPush.mockClear();
  });

  it("orders meta+tags row, then title and summary", async () => {
    articles.value = [sampleArticle];
    total.value = 1;
    totalPages.value = 1;
    const wrapper = mountPage();
    await flushPromises();

    const card = wrapper.get("a.card-as-link");
    const text = card.text();
    const sourceIdx = text.indexOf("Example Source");
    const titleIdx = text.indexOf("Scan-friendly title");
    const summaryIdx = text.indexOf("A concise summary for hiring managers.");
    const tagIdx = text.indexOf("#python");

    expect(card.attributes("href")).toBe("/news/sample-article");
    expect(card.find("a").exists()).toBe(false);
    expect(sourceIdx).toBeGreaterThanOrEqual(0);
    expect(tagIdx).toBeGreaterThan(sourceIdx);
    expect(titleIdx).toBeGreaterThan(tagIdx);
    expect(summaryIdx).toBeGreaterThan(titleIdx);
    expect(card.find(".news-tag-chip").exists()).toBe(true);
    expect(card.find("h2").text()).toContain("Scan-friendly title");
  });

  it("navigates from a click anywhere on the tile", async () => {
    articles.value = [sampleArticle];
    total.value = 1;
    totalPages.value = 1;
    const wrapper = mountPage();
    await flushPromises();

    const card = wrapper.get("a.card-as-link");
    await card.trigger("click");

    expect(routerPush).toHaveBeenCalledWith({
      name: "news-article",
      params: { slug: "sample-article" },
    });
  });

  it("keeps loading, error, and empty states", async () => {
    listLoading.value = true;
    let wrapper = mountPage();
    await flushPromises();
    expect(wrapper.find('[aria-busy="true"]').attributes("aria-label")).toBe("Loading news");

    listLoading.value = false;
    listError.value = "Failed to load news";
    wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text()).toContain("Failed to load news");

    listError.value = null;
    articles.value = [];
    wrapper = mountPage();
    await flushPromises();
    expect(wrapper.text().toLowerCase()).toContain("no news yet");
  });
});
